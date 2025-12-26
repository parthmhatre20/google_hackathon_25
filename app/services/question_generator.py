from app.models import GenerateQuestionsRequest, GenerateQuestionsResponse, GeneratedQuestion
from app.config import settings
import json
import re

class QuestionGeneratorService:
    def __init__(self):
        self.model = None
        
        # Try to initialize Gemini
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Question Generator service initialized successfully!")
            except Exception as e:
                print(f"⚠️  Could not initialize Question Generator: {e}")
        else:
            print("⚠️  Question Generator: Gemini API key not found")
    
    async def generate_questions(self, request: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
        """Generate personalized interview questions based on resume and domain"""
        
        if not self.model:
            raise Exception("Gemini AI not configured. Please add your Gemini API key to the .env file.")
        
        try:
            prompt = f"""
You are an expert technical interviewer. Generate personalized interview questions for a candidate.

**Candidate Domain:** {request.domain}

**Candidate Resume:**
{request.resume_text}

**Task:**
Generate {request.num_questions} interview questions in JSON format:
1. 2 questions from their projects/experience mentioned in resume
2. 2 questions testing core {request.domain} knowledge
3. 1 behavioral/situational question

**Output Format (MUST be valid JSON):**
{{
    "questions": [
        {{
            "question_id": "q1",
            "question_text": "Based on your carbon emission calculator project, how did you...",
            "category": "project-based",
            "reasoning": "Tests understanding of their Django project"
        }},
        {{
            "question_id": "q2",
            "question_text": "Explain how you would optimize database queries in Django",
            "category": "domain-knowledge",
            "reasoning": "Core web development skill"
        }}
    ],
    "resume_summary": "Brief 1-line summary of candidate's background"
}}

**Requirements:**
- Make questions specific to their experience
- Keep questions clear and professional
- Vary difficulty levels
- Focus on practical scenarios
- Category should be: "project-based", "domain-knowledge", or "behavioral"

Return ONLY the JSON, no additional text.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse AI response as JSON")
            
            # Parse questions
            questions = []
            for idx, q in enumerate(data.get('questions', []), 1):
                questions.append(GeneratedQuestion(
                    question_id=q.get('question_id', f'q{idx}'),
                    question_text=q.get('question_text', ''),
                    category=q.get('category', 'general'),
                    reasoning=q.get('reasoning')
                ))
            
            # If we didn't get enough questions, add fallback
            if len(questions) < request.num_questions:
                questions.extend(self._get_fallback_questions(request.domain, request.num_questions - len(questions)))
            
            return GenerateQuestionsResponse(
                domain=request.domain,
                questions=questions[:request.num_questions],
                resume_summary=data.get('resume_summary')
            )
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            # Return fallback questions
            return GenerateQuestionsResponse(
                domain=request.domain,
                questions=self._get_fallback_questions(request.domain, request.num_questions),
                resume_summary="Unable to analyze resume at this time"
            )
    
    def _get_fallback_questions(self, domain: str, num: int) -> list:
        """Fallback questions if AI fails"""
        fallback = [
            GeneratedQuestion(
                question_id=f"fallback_q1",
                question_text=f"Tell me about your experience with {domain}.",
                category="general"
            ),
            GeneratedQuestion(
                question_id=f"fallback_q2",
                question_text=f"What projects have you worked on related to {domain}?",
                category="project-based"
            ),
            GeneratedQuestion(
                question_id=f"fallback_q3",
                question_text="Describe a challenging technical problem you solved.",
                category="behavioral"
            ),
            GeneratedQuestion(
                question_id=f"fallback_q4",
                question_text=f"What are the key skills needed in {domain}?",
                category="domain-knowledge"
            ),
            GeneratedQuestion(
                question_id=f"fallback_q5",
                question_text="How do you stay updated with the latest technologies?",
                category="behavioral"
            ),
        ]
        return fallback[:num]

question_generator_service = QuestionGeneratorService()
