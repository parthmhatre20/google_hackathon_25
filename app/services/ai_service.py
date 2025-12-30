from app.models import AnalysisResponse, FillerWordsAnalysis
from app.config import settings
import json
import re

class AIService:
    def __init__(self):
        self.model = None
        self.api_keys = settings.get_api_keys_list()
        self.current_key_index = 0
        self.clients = {}  # Cache clients for each key
        self.all_keys_exhausted = False  # Safety: stop trying after all quotas hit
        self.quota_exhausted_keys = set()  # Track which keys hit quota
        
        # Try to initialize Gemini with all available keys
        if self.api_keys:
            try:
                from google import genai
                # Initialize clients for all keys
                for i, key in enumerate(self.api_keys):
                    try:
                        self.clients[i] = genai.Client(api_key=key)
                    except Exception as e:
                        print(f"⚠️  Failed to initialize client for key #{i+1}: {e}")
                
                if self.clients:
                    self.client = self.clients[0]
                    self.model_name = 'gemini-2.5-flash'  # Latest stable model
                    print(f"✅ Gemini AI service initialized with {len(self.clients)} API key(s)!")
                    print(f"   Using model: {self.model_name}")
                else:
                    print("❌ All API keys failed to initialize")
                    self.client = None
            except Exception as e:
                print(f"⚠️  Could not initialize Gemini: {e}")
                self.client = None
        else:
            print("⚠️  No Gemini API keys found in .env file")
            print("   Add GEMINI_API_KEY or GEMINI_API_KEYS (comma-separated)")
            self.client = None
        
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'basically', 
            'actually', 'literally', 'kind of', 'sort of', 'i mean',
            'you see', 'right', 'okay', 'well'
        ]
    
    def count_filler_words(self, transcription: str) -> dict:
        """Count filler words in transcription"""
        transcription_lower = transcription.lower()
        found_fillers = []
        
        for filler in self.filler_words:
            count = transcription_lower.count(filler)
            if count > 0:
                found_fillers.extend([filler] * count)
        
        total_words = len(transcription.split())
        filler_count = len(found_fillers)
        percentage = (filler_count / total_words * 100) if total_words > 0 else 0
        
        return {
            'count': filler_count,
            'percentage': round(percentage, 2),
            'words': found_fillers  # Changed from 'list' to 'words'
        }
    
    def rotate_api_key(self) -> bool:
        """Rotate to next API key. Returns True if rotation successful, False if no more keys."""
        if len(self.clients) <= 1:
            return False  # No other keys to try
        
        # Try next key
        self.current_key_index = (self.current_key_index + 1) % len(self.clients)
        
        if self.current_key_index in self.clients:
            self.client = self.clients[self.current_key_index]
            print(f"🔄 Rotated to API key #{self.current_key_index + 1}")
            return True
        
        return False
    
    async def analyze_answer(self, transcription: str, question_text: str) -> AnalysisResponse:
        """Analyze interview answer with automatic API key rotation on quota errors"""
        if not self.client:
            print("❌ No Gemini client available")
            return self._create_fallback_response()
        
        # Safety: Don't make API calls if all quotas are exhausted
        if self.all_keys_exhausted:
            print("⛔ All API key quotas exhausted - using fallback (no API calls made)")
            return self._create_fallback_response()
        
        # Try with current key, rotate on quota error
        max_retries = len(self.clients)
        attempt = 0
        
        while attempt < max_retries:
            try:
                # Analyze filler words
                filler_analysis = self.count_filler_words(transcription)
                
                prompt = f"""Rate this interview answer. Be concise.

Q: {question_text}
A: {transcription}

JSON only:
{{"overall_score":<0-100>,"content_score":<0-100>,"clarity_score":<0-100>,"confidence_score":<0-100>,"strengths":["point1","point2"],"improvements":["tip1","tip2"]}}"""
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                response_text = response.text.strip()
                
                # Extract JSON from response
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    
                    strengths = analysis_data.get('strengths', ['Answer recorded successfully'])
                    improvements = analysis_data.get('improvements', ['Try to elaborate more on your points'])
                    
                    return AnalysisResponse(
                        overall_score=analysis_data.get('overall_score', 70),
                        content_score=analysis_data.get('content_score', 70),
                        clarity_score=analysis_data.get('clarity_score', 70),
                        confidence_score=analysis_data.get('confidence_score', 70),
                        strengths=strengths,
                        improvements=improvements,
                        filler_words=filler_analysis,
                        detailed_feedback=f"Strengths: {', '.join(strengths)}. Areas for improvement: {', '.join(improvements)}."
                    )
                else:
                    raise ValueError("No valid JSON in response")
                    
            except Exception as e:
                error_str = str(e)
                print(f"❌ ERROR in AI analysis (key #{self.current_key_index + 1}): {error_str}")
                
                # Check if it's a quota error (429)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                    print(f"   ⚠️  Quota exceeded for key #{self.current_key_index + 1}")
                    
                    # Mark this key as exhausted
                    self.quota_exhausted_keys.add(self.current_key_index)
                    
                    # Try to rotate to next key
                    if self.rotate_api_key():
                        attempt += 1
                        print(f"   🔄 Retrying with key #{self.current_key_index + 1}...")
                        continue  # Retry with new key
                    else:
                        # All keys tried and failed
                        self.all_keys_exhausted = True
                        print("   ⛔ ALL API KEYS EXHAUSTED - No more API calls will be made")
                        print("   💡 Free tier quota limits reached. System will use fallback responses.")
                        print("   ℹ️  No charges will occur - free tier just stops working.")
                        break
                else:
                    # Non-quota error, don't retry
                    print(f"   Non-quota error, not retrying")
                    break
        
        # All keys exhausted or non-quota error
        print("   Returning fallback response (all 60s).")
        return self._create_fallback_response()
    
    def _create_fallback_response(self) -> AnalysisResponse:
        """Create fallback response when AI fails"""
        warning_msg = 'All API keys exhausted or failed. Using mock scores.' if self.all_keys_exhausted else 'Gemini API failed. Check backend logs.'
        
        improvements = [
            'Free tier quota exhausted for all keys' if self.all_keys_exhausted else 'Check API keys',
            'No charges will occur - free tier has limits',
            'Wait 24 hours for quota reset or add more API keys'
        ]
        
        return AnalysisResponse(
            overall_score=60,
            content_score=60,
            clarity_score=60,
            confidence_score=60,
            strengths=['⚠️ USING MOCK DATA - Gemini API unavailable'],
            improvements=improvements,
            filler_words={'count': 0, 'percentage': 0.0, 'words': []},
            detailed_feedback=f"{warning_msg} {' '.join(improvements)}"
        )


ai_service = AIService()
