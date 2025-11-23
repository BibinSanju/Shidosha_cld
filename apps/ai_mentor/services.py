"""
AI Mentor Service - Core logic for interacting with Claude AI.

This service wraps the Anthropic Claude API and provides:
- Context-aware prompt building using student data, progress, and course content
- Structured response parsing
- Conversation memory management
- Error handling and fallbacks
"""
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from anthropic import Anthropic, AnthropicError

logger = logging.getLogger(__name__)


class MentorService:
    """
    Service class for AI mentor interactions.
    Handles all Claude API calls with context-aware prompting.
    """

    def __init__(self):
        """Initialize the Anthropic client."""
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured in settings")

        self.client = Anthropic(api_key=api_key)
        self.model = settings.AI_MENTOR_MODEL
        self.max_tokens = settings.AI_MENTOR_MAX_TOKENS
        self.temperature = settings.AI_MENTOR_TEMPERATURE

    def build_system_prompt(self) -> str:
        """
        Build the system prompt that defines the AI mentor's role and behavior.
        """
        return """You are Shidosha, an AI-powered learning mentor for students.

Your role:
- Help students understand course concepts step by step
- Provide personalized guidance based on their learning history and progress
- Encourage critical thinking by asking questions rather than giving direct answers
- Suggest relevant lessons, practice exercises, or review material
- Be patient, supportive, and adapt to each student's learning style
- Never provide complete solutions to assignments - guide students to discover answers

Guidelines:
- Always explain concepts clearly with examples
- Break down complex topics into digestible parts
- Reference specific lessons or course materials when relevant
- Suggest actionable next steps (e.g., "Try reviewing Module 2, Lesson 3")
- If a student is struggling, recommend reviewing prerequisite material
- Celebrate progress and encourage continuous learning
- If you don't know something or it's outside the course scope, say so honestly

Context awareness:
- Use the student's profile information (year, branch, interests, goals)
- Consider their current progress in the course
- Reference their recent quiz scores and weak areas
- Adapt difficulty based on their performance history

Output format:
- Provide clear, structured responses
- Use markdown for formatting when helpful
- Include specific suggestions (lesson IDs, quiz IDs) when appropriate
"""

    def build_context(
        self,
        student,
        course=None,
        lesson=None,
        session_messages: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Build rich context data for the AI mentor.

        Args:
            student: User object (student)
            course: Course object (optional)
            lesson: Lesson object (optional)
            session_messages: Previous messages in the session (optional)

        Returns:
            Dict containing structured context data
        """
        context = {
            "student": {
                "username": student.username,
                "name": student.get_full_name(),
            }
        }

        # Add student profile data
        if hasattr(student, 'student_profile'):
            profile = student.student_profile
            context["student"].update({
                "institution": profile.institution,
                "year_of_study": profile.year_of_study,
                "branch": profile.branch,
                "interests": profile.interests,
                "learning_goals": profile.learning_goals,
                "learning_style": profile.preferred_learning_style,
                "level": profile.level,
                "total_points": profile.total_points,
            })

        # Add course context
        if course:
            from apps.progress.models import Enrollment

            context["course"] = {
                "title": course.title,
                "difficulty": course.difficulty_level,
            }

            # Add enrollment and progress data
            try:
                enrollment = Enrollment.objects.get(student=student, course=course)
                context["progress"] = {
                    "completion_percentage": float(enrollment.progress_percentage),
                    "status": enrollment.status,
                }

                # Get current lesson
                current = enrollment.current_lesson
                if current:
                    context["progress"]["current_lesson"] = {
                        "title": current.title,
                        "module": current.module.title,
                    }
            except Enrollment.DoesNotExist:
                context["progress"] = {"enrolled": False}

        # Add specific lesson context
        if lesson:
            context["current_lesson"] = {
                "title": lesson.title,
                "description": lesson.description,
                "content_type": lesson.content_type,
                "module": lesson.module.title,
            }

            # Check if student has attempted this lesson
            from apps.progress.models import LessonProgress
            try:
                progress = LessonProgress.objects.get(student=student, lesson=lesson)
                context["current_lesson"]["progress"] = {
                    "completed": progress.is_completed,
                    "completion_percentage": float(progress.completion_percentage),
                    "time_spent_seconds": progress.time_spent_seconds,
                }
            except LessonProgress.DoesNotExist:
                context["current_lesson"]["progress"] = {"started": False}

        # Add recent quiz performance (if any)
        # TODO: Add when assessments are implemented

        return context

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format the context dictionary into a readable string for the prompt.
        """
        lines = ["Current Context:"]

        # Student info
        student = context.get("student", {})
        lines.append(f"\nStudent: {student.get('name', 'Unknown')}")
        if student.get("branch"):
            lines.append(f"Branch/Major: {student.get('branch')}")
        if student.get("year_of_study"):
            lines.append(f"Year of Study: {student.get('year_of_study')}")
        if student.get("learning_goals"):
            lines.append(f"Learning Goals: {student.get('learning_goals')}")

        # Course info
        if "course" in context:
            course = context["course"]
            lines.append(f"\nCourse: {course.get('title')}")
            lines.append(f"Difficulty: {course.get('difficulty')}")

        # Progress info
        if "progress" in context:
            progress = context["progress"]
            if progress.get("enrolled", True):
                lines.append(f"\nCourse Progress: {progress.get('completion_percentage', 0):.1f}%")
                if "current_lesson" in progress:
                    curr = progress["current_lesson"]
                    lines.append(f"Current Position: {curr.get('module')} - {curr.get('title')}")

        # Current lesson
        if "current_lesson" in context:
            lesson = context["current_lesson"]
            lines.append(f"\nCurrent Lesson: {lesson.get('title')}")
            lines.append(f"Module: {lesson.get('module')}")
            if lesson.get("progress", {}).get("started"):
                lp = lesson["progress"]
                lines.append(f"Lesson Progress: {lp.get('completion_percentage', 0):.1f}%")

        return "\n".join(lines)

    def ask_mentor(
        self,
        student,
        message: str,
        course=None,
        lesson=None,
        session_messages: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a question to the AI mentor and get a response.

        Args:
            student: User object (student)
            message: Student's question/message
            course: Course object (optional)
            lesson: Lesson object (optional)
            session_messages: Previous messages in the session (optional)

        Returns:
            Dict with:
                - content: AI response text
                - context: Context data used
                - model: Model name used
                - tokens_used: Number of tokens
                - suggested_actions: List of suggested actions
        """
        try:
            # Build context
            context = self.build_context(student, course, lesson, session_messages)
            context_str = self.format_context_for_prompt(context)

            # Build messages list
            messages = []

            # Add conversation history if available
            if session_messages:
                for msg in session_messages[-10:]:  # Keep last 10 messages for context
                    messages.append({
                        "role": "user" if msg["role"] == "student" else "assistant",
                        "content": msg["content"]
                    })

            # Add context and current message
            user_message = f"{context_str}\n\nStudent Question: {message}"
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Call Claude API
            logger.info(f"Calling Claude API for student {student.username}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.build_system_prompt(),
                messages=messages
            )

            # Extract response
            assistant_message = response.content[0].text

            # Parse suggested actions (simple heuristic for now)
            suggested_actions = self._extract_suggested_actions(assistant_message)

            result = {
                "content": assistant_message,
                "context": context,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "suggested_actions": suggested_actions,
            }

            logger.info(f"Mentor response generated successfully ({result['tokens_used']} tokens)")
            return result

        except AnthropicError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return {
                "content": "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
                "context": {},
                "model": self.model,
                "tokens_used": 0,
                "suggested_actions": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in ask_mentor: {str(e)}")
            return {
                "content": "I encountered an unexpected error. Please contact support if this persists.",
                "context": {},
                "model": self.model,
                "tokens_used": 0,
                "suggested_actions": [],
                "error": str(e)
            }

    def _extract_suggested_actions(self, response_text: str) -> List[str]:
        """
        Extract suggested actions from the AI response.
        This is a simple heuristic - can be improved with structured output.
        """
        actions = []

        # Look for common action phrases
        action_keywords = [
            "try reviewing",
            "take the quiz",
            "practice",
            "move to the next lesson",
            "revisit",
        ]

        response_lower = response_text.lower()
        for keyword in action_keywords:
            if keyword in response_lower:
                actions.append(keyword)

        return actions


# Singleton instance
_mentor_service = None


def get_mentor_service() -> MentorService:
    """Get or create the mentor service singleton."""
    global _mentor_service
    if _mentor_service is None:
        _mentor_service = MentorService()
    return _mentor_service
