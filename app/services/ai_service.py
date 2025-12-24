from app.models import AnalysisResponse, FillerWordsAnalysis
from app.config import settings
import json
import re

class AIService:
    def __init__(self):
        self.model = None
        
        # Try to initialize Gemini
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI service initialized successfully!")
            except Exception as e:
                print(f"⚠️  Could not initialize Gemini: {e}")
        else:
            print("⚠️  Gemini API key not found in .env file")
        
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'so', 'basically', 
            'actually', 'literally', 'kind of', 'sort of', 'i mean'
        ]
    
    def count_filler_words(self, transcription: str) -> FillerWordsAnalysis:
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
        
        return FillerWordsAnalysis(
            count=filler_count,
            words=list(set(found_fillers)),
            percentage=round(percentage, 2)
        )
    
    async def analyze_answer(self, transcription: str, question_text: str) -> AnalysisResponse:
        """Analyze interview answer using Gemini API"""
        
        if not self.model:
            raise Exception("Gemini AI not configured. Please add your Gemini API key to the .env file.")
        
        try:
            filler_analysis = self.count_filler_words(transcription)
            
            prompt = f"""
You are an expert interview coach. Analyze this interview answer and provide detailed feedback.

**Question:** {question_text}

**Answer:** {transcription}

Provide your analysis in the following JSON format:
{{
    "content_score": <0-100>,
    "clarity_score": <0-100>,
    "confidence_score": <0-100>,
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["improvement1", "improvement2", "improvement3"],
    "detailed_feedback": "Detailed paragraph explaining the scores and feedback"
}}

Scoring criteria:
- **Content Score**: Relevance, depth, structure, examples
- **Clarity Score**: Clear communication, logical flow, coherence
- **Confidence Score**: Assertiveness, reduced hesitation, professional tone

Provide 3 specific strengths and 3 actionable improvements. Be encouraging but honest.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse AI response")
            
            # Calculate overall score
            content_score = analysis_data.get('content_score', 70)
            clarity_score = analysis_data.get('clarity_score', 70)
            confidence_score = analysis_data.get('confidence_score', 70)
            
            # Adjust confidence based on filler words
            filler_penalty = min(filler_analysis.percentage, 15)
            confidence_score = max(confidence_score - filler_penalty, 0)

            
            overall_score = (content_score + clarity_score + confidence_score) / 3
            
            return AnalysisResponse(
                overall_score=round(overall_score, 1),
                content_score=round(content_score, 1),
                clarity_score=round(clarity_score, 1),
                confidence_score=round(confidence_score, 1),
                filler_words=filler_analysis,
                strengths=analysis_data.get('strengths', []),
                improvements=analysis_data.get('improvements', []),
                detailed_feedback=analysis_data.get('detailed_feedback', '')
            )
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            # Fallback response
            filler_analysis = self.count_filler_words(transcription)
            return AnalysisResponse(
                overall_score=60.0,
                content_score=60.0,
                clarity_score=60.0,
                confidence_score=60.0,
                filler_words=filler_analysis,
                strengths=["Answer recorded successfully"],
                improvements=["Try to be more specific", "Add concrete examples", "Reduce filler words"],
                detailed_feedback="Your answer has been recorded. Keep practicing to improve!"
            )

ai_service = AIService()