"""
ai_service.py — Mistral AI Integration Service
=================================================
WHY THIS FILE EXISTS:
    This is the BRAIN of the application. It handles ALL communication
    with the Mistral AI API.

    Instead of putting AI calls directly in your Flask routes (app.py),
    we create a dedicated service class. This follows the
    'Single Responsibility Principle':
        - app.py handles HTTP requests/responses
        - ai_service.py handles AI logic

    BENEFITS:
        1. Easy to swap AI providers (e.g., switch from Mistral to OpenAI)
        2. Centralized prompt engineering
        3. Easy to test — mock this class in unit tests
        4. Reusable across different routes

METHODS:
    - chat()                        → General career chat
    - analyze_resume()              → Resume feedback & scoring
    - generate_interview_questions() → Role-specific interview prep
    - generate_career_roadmap()     → Step-by-step career path
"""

try:
    from mistralai import Mistral
except ImportError:
    from mistralai.client import Mistral



class AIService:
    """Wraps all Mistral AI API interactions."""

    def __init__(self, api_key, model='mistral-small-latest'):
        """
        Initialize the Mistral client.

        Args:
            api_key (str): Your Mistral API key from console.mistral.ai
            model (str): Which Mistral model to use
        """
        self.client = Mistral(api_key=api_key)
        self.model = model

    def chat(self, messages, feature='chat'):
        """
        Send a chat message to Mistral and get a response.

        WHY system prompts?
            The system prompt tells the AI WHO it is and HOW to behave.
            Different features get different system prompts so the AI
            responds appropriately for each context.

        Args:
            messages (list): List of {'role': 'user/assistant', 'content': '...'}
            feature (str): Which feature is calling (chat/resume/interview/roadmap)

        Returns:
            str: The AI's response text
        """
        system_prompts = {
            'chat': (
                "You are AI Career Connect, a professional career counselor AI. "
                "You help users with career advice, job searching, skill development, "
                "and professional growth. Be encouraging, specific, and actionable. "
                "Always provide concrete next steps."
            ),
            'resume': (
                "You are an expert resume reviewer and career coach. "
                "Analyze resumes thoroughly, provide specific improvement suggestions, "
                "score them out of 100, and highlight strengths and weaknesses. "
                "Format your response with clear sections."
            ),
            'interview': (
                "You are an expert interview coach. Generate relevant, challenging "
                "interview questions based on the job role and experience level. "
                "Include a mix of technical, behavioral, and situational questions. "
                "Provide brief tips on how to answer each question."
            ),
            'roadmap': (
                "You are a career planning expert. Create detailed, step-by-step "
                "career roadmaps. Include specific skills to learn, certifications, "
                "timeline estimates, resources, and milestones. Be realistic and "
                "practical. Format as a clear progression path."
            ),
        }

        # Build the full message list with system prompt at the start
        full_messages = [
            {'role': 'system', 'content': system_prompts.get(feature, system_prompts['chat'])}
        ] + messages

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=full_messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}"

    def analyze_resume(self, resume_text):
        """
        Analyze a resume and return structured feedback.

        Args:
            resume_text (str): The full text of the resume

        Returns:
            str: Detailed analysis with score and suggestions
        """
        messages = [
            {
                'role': 'user',
                'content': (
                    f"Please analyze the following resume thoroughly. Provide:\n"
                    f"1. Overall Score (out of 100)\n"
                    f"2. Strengths\n"
                    f"3. Weaknesses\n"
                    f"4. Specific improvement suggestions\n"
                    f"5. ATS (Applicant Tracking System) compatibility tips\n\n"
                    f"RESUME:\n{resume_text}"
                )
            }
        ]
        return self.chat(messages, feature='resume')

    def generate_interview_questions(self, role, experience_level='mid', num_questions=10):
        """
        Generate interview questions for a specific role.

        Args:
            role (str): Job title (e.g., 'Python Developer')
            experience_level (str): 'junior', 'mid', or 'senior'
            num_questions (int): How many questions to generate

        Returns:
            str: Formatted list of interview questions with tips
        """
        messages = [
            {
                'role': 'user',
                'content': (
                    f"Generate {num_questions} interview questions for a "
                    f"{experience_level}-level {role} position.\n\n"
                    f"For each question, provide:\n"
                    f"- The question\n"
                    f"- Why interviewers ask this\n"
                    f"- A tip for answering effectively\n\n"
                    f"Include a mix of technical, behavioral, and situational questions."
                )
            }
        ]
        return self.chat(messages, feature='interview')

    def generate_career_roadmap(self, current_role, target_role, experience_years=0):
        """
        Generate a career roadmap from current position to target role.

        Args:
            current_role (str): User's current role (or 'student')
            target_role (str): Desired career goal
            experience_years (int): Years of experience

        Returns:
            str: Detailed career roadmap with timeline and milestones
        """
        messages = [
            {
                'role': 'user',
                'content': (
                    f"Create a detailed career roadmap:\n"
                    f"- Current Position: {current_role}\n"
                    f"- Target Role: {target_role}\n"
                    f"- Years of Experience: {experience_years}\n\n"
                    f"Include:\n"
                    f"1. Phase-by-phase progression (with timeline)\n"
                    f"2. Skills to learn at each phase\n"
                    f"3. Recommended certifications\n"
                    f"4. Projects to build\n"
                    f"5. Resources (courses, books, websites)\n"
                    f"6. Milestones to track progress"
                )
            }
        ]
        return self.chat(messages, feature='roadmap')
