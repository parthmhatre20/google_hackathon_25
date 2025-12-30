from app.models import GenerateQuestionsRequest, GenerateQuestionsResponse, GeneratedQuestion
from app.config import settings
import json
import re

class QuestionGeneratorService:
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
                        print(f"⚠️  Failed to init question gen client for key #{i+1}: {e}")
                
                if self.clients:
                    self.client = self.clients[0]
                    self.model_name = 'gemini-2.5-flash'  # Latest stable model
                    print(f"✅ Question Generator initialized with {len(self.clients)} API key(s)!")
                else:
                    print("❌ All API keys failed for question generator")
                    self.client = None
            except Exception as e:
                print(f"⚠️  Could not initialize Question Generator: {e}")
                self.client = None
        else:
            print("⚠️  Question Generator: No Gemini API keys found")
            self.client = None
    
    def _get_hardcoded_questions(self, domain: str) -> GenerateQuestionsResponse:
        """Fallback hardcoded questions when AI fails"""
        questions_map = {
            "Frontend Engineer": [
                {"text": "Tell me about your experience with Frontend Engineer.", "reasoning": "Assess domain knowledge"},
                {"text": "What projects have you worked on related to Frontend Engineer?", "reasoning": "Understand practical experience"},
                {"text": "Describe a challenging technical problem you solved.", "reasoning": "Problem-solving skills"},
                {"text": "How do you stay updated with industry trends?", "reasoning": "Continuous learning"},
                {"text": "Where do you see yourself in 5 years?", "reasoning": "Career goals"}
            ],
            "Backend Engineer": [
                {"text": "Explain your experience with server-side technologies.", "reasoning": "Technical background"},
                {"text": "How do you handle database optimization?", "reasoning": "Performance skills"},
                {"text": "Describe your API design approach.", "reasoning": "Architecture knowledge"},
                {"text": "What's your experience with microservices?", "reasoning": "Modern architecture"},
                {"text": "How do you ensure code quality?", "reasoning": "Best practices"}
            ]
        }
        
        default_questions = [
            {"text": f"Tell me about your experience with {domain}.", "reasoning": "Domain knowledge"},
            {"text": f"What projects have you worked on in {domain}?", "reasoning": "Practical experience"},
            {"text": "Describe a challenging problem you solved.", "reasoning": "Problem-solving"},
            {"text": "How do you stay current in your field?", "reasoning": "Learning mindset"},
            {"text": "What are your career goals?", "reasoning": "Future planning"}
        ]
        
        questions_data = questions_map.get(domain, default_questions)
        
        return GenerateQuestionsResponse(
            domain=domain,
            questions=[
                GeneratedQuestion(
                    question_id=f"q_{i+1}",
                    question_text=q["text"],
                    category="general",
                    reasoning=q["reasoning"]
                )
                for i, q in enumerate(questions_data)
            ]
        )
    
    def rotate_api_key(self) -> bool:
        """Rotate to next API key. Returns True if rotation successful, False if no more keys."""
        if len(self.clients) <= 1:
            return False  # No other keys to try
        
        # Try next key
        self.current_key_index = (self.current_key_index + 1) % len(self.clients)
        
        if self.current_key_index in self.clients:
            self.client = self.clients[self.current_key_index]
            print(f"🔄 Question Gen rotated to API key #{self.current_key_index + 1}")
            return True
        
        return False
    
    async def generate_questions(self, request: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
        """Generate interview questions with automatic API key rotation on quota errors"""
        if not self.client:
            print("No Gemini client, using hardcoded questions")
            return self._get_hardcoded_questions(request.domain)
        
        # Safety: Don't make API calls if all quotas are exhausted
        if self.all_keys_exhausted:
            print("⛔ All API key quotas exhausted - using hardcoded questions (no API calls made)")
            return self._get_hardcoded_questions(request.domain)
        
        # Try with current key, rotate on quota error
        max_retries = len(self.clients)
        attempt = 0
        
        while attempt < max_retries:
            try:
                # Build context from resume
                bg = f"\nCandidate background: {request.resume_text[:500]}" if request.resume_text else ""
                
                prompt = f"""Generate 5 interview questions for a {request.domain} position.{bg}

Requirements:
1. Q1: Warm intro ("Tell me about yourself...")
2. Q2-Q4: Technical questions specific to {request.domain} (concepts, problem-solving, real scenarios)
3. Q5: Experience/projects question

Return JSON:
{{
  "questions": [
    {{"question_text": "Your question here?", "reasoning": "Brief reason"}}
  ]
}}

Make questions sound natural, like a real interviewer."""

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                response_text = response.text.strip()
                
                # Extract JSON - handle nested objects properly
                # Try to find JSON block with questions array
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end+1]
                    data = json.loads(json_str)
                    questions = []
                    
                    for i, q in enumerate(data.get('questions', [])[:5]):
                        questions.append(GeneratedQuestion(
                            question_id=f"q_{i+1}",
                            question_text=q.get('question_text', f'Question {i+1}'),
                            category="technical",
                            reasoning=q.get('reasoning', '')
                        ))
                    
                    if len(questions) == 5:
                        return GenerateQuestionsResponse(domain=request.domain, questions=questions)
                    else:
                        raise ValueError(f"Only got {len(questions)} questions, need 5")
                else:
                    raise ValueError("No valid JSON in response")
                    
            except Exception as e:
                error_str = str(e)
                print(f"Error generating questions (key #{self.current_key_index + 1}): {error_str}")
                
                # Check if it's a quota error (429)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                    print(f"   ⚠️  Quota exceeded for key #{self.current_key_index + 1}")
                    
                    # Mark this key as exhausted
                    self.quota_exhausted_keys.add(self.current_key_index)
                    
                    # Try to rotate to next key
                    if self.rotate_api_key():
                        attempt += 1
                        print(f"   🔄 Retrying question generation with key #{self.current_key_index + 1}...")
                        continue  # Retry with new key
                    else:
                        # All keys tried and failed
                        self.all_keys_exhausted = True
                        print("   ⛔ ALL API KEYS EXHAUSTED - Using hardcoded questions only")
                        print("   💡 Free tier quota limits reached. No charges will occur.")
                        break
                else:
                    # Non-quota error, don't retry
                    print(f"   Non-quota error, using fallback")
                    break
        
        # All keys exhausted or error - use hardcoded questions
        print("Using hardcoded questions as fallback")
        return self._get_hardcoded_questions(request.domain)


question_generator_service = QuestionGeneratorService()
