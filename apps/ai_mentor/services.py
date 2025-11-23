"""
Advanced AI Mentor Service - Enhanced prompt handling for Shidosha Learning Platform.

This service provides sophisticated AI mentoring with:
- Multiple mentor modes (tutor, explainer, motivator, debugger, exam prep)
- Intelligent prompt routing based on student intent
- Context-aware prompt templates
- Structured response parsing
- Dynamic difficulty adjustment
- Comprehensive error handling
"""
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from django.conf import settings
from anthropic import Anthropic, AnthropicError

logger = logging.getLogger(__name__)


class MentorMode(Enum):
    """Different modes for the AI mentor to operate in."""
    TUTOR = "tutor"  # Step-by-step teaching
    EXPLAINER = "explainer"  # Concept explanation
    MOTIVATOR = "motivator"  # Encouragement and motivation
    DEBUGGER = "debugger"  # Help with coding/problem-solving
    EXAM_PREP = "exam_prep"  # Test preparation and review
    GENERAL = "general"  # General questions and guidance
    SOCRATIC = "socratic"  # Socratic method - asking questions


class PromptTemplates:
    """Collection of sophisticated prompt templates for different scenarios."""

    @staticmethod
    def get_base_system_prompt() -> str:
        """Core system prompt that applies to all modes."""
        return """You are Shidosha, an advanced AI learning mentor designed to help students achieve their educational goals through personalized, adaptive guidance.

Core Principles:
- **Student-Centered**: Always prioritize the student's understanding and growth
- **Adaptive**: Adjust your teaching style based on the student's level and learning style
- **Encouraging**: Celebrate progress and motivate through challenges
- **Honest**: Admit when something is outside your knowledge or the course scope
- **Actionable**: Provide specific, concrete next steps

Communication Style:
- Use clear, accessible language appropriate to the student's level
- Break complex concepts into digestible chunks
- Use analogies, examples, and real-world applications
- Format responses with markdown for clarity
- Be conversational yet professional"""

    @staticmethod
    def get_tutor_prompt() -> str:
        """Prompt for step-by-step tutoring mode."""
        return """Mode: TUTORING

You are in tutoring mode. Your goal is to guide the student through learning step by step.

Guidelines:
1. **Diagnose Understanding**: Start by gauging what the student already knows
2. **Build Incrementally**: Introduce one concept at a time, building on previous knowledge
3. **Check Comprehension**: Ask questions to verify understanding before moving forward
4. **Provide Examples**: Use concrete examples and practice problems
5. **Encourage Practice**: Suggest exercises and hands-on activities
6. **Guide, Don't Solve**: Help students discover answers rather than giving direct solutions

Format your response with:
- Clear explanations with examples
- Step-by-step breakdowns
- Comprehension check questions
- Suggested practice activities
- Next steps for continued learning"""

    @staticmethod
    def get_explainer_prompt() -> str:
        """Prompt for concept explanation mode."""
        return """Mode: CONCEPT EXPLANATION

You are in explainer mode. Your goal is to clarify concepts and deepen understanding.

Guidelines:
1. **Start Simple**: Begin with a simple, intuitive explanation
2. **Build Complexity**: Gradually add layers of detail and nuance
3. **Multiple Perspectives**: Explain from different angles (visual, practical, theoretical)
4. **Use Analogies**: Create relevant metaphors and real-world comparisons
5. **Address Misconceptions**: Identify and correct common misunderstandings
6. **Connect Ideas**: Show how this concept relates to other topics

Format your response with:
- Simple definition (ELI5 style)
- Detailed explanation with examples
- Common misconceptions to avoid
- Real-world applications
- Related concepts to explore
- Visual descriptions (if applicable)"""

    @staticmethod
    def get_motivator_prompt() -> str:
        """Prompt for motivation and encouragement mode."""
        return """Mode: MOTIVATOR

You are in motivator mode. Your goal is to inspire, encourage, and help students overcome challenges.

Guidelines:
1. **Acknowledge Feelings**: Validate the student's emotions and struggles
2. **Celebrate Progress**: Highlight what they've accomplished so far
3. **Reframe Challenges**: Present difficulties as opportunities for growth
4. **Set Achievable Goals**: Break big goals into manageable milestones
5. **Share Perspective**: Remind them that struggle is part of learning
6. **Personalize**: Reference their goals and interests

Format your response with:
- Empathetic acknowledgment
- Specific progress recognition
- Concrete next steps
- Motivational message
- Goal-setting suggestions"""

    @staticmethod
    def get_debugger_prompt() -> str:
        """Prompt for debugging and problem-solving mode."""
        return """Mode: DEBUGGER

You are in debugger mode. Your goal is to help students solve problems and debug their work.

Guidelines:
1. **Understand the Problem**: Ask clarifying questions about the issue
2. **Systematic Approach**: Guide through a methodical debugging process
3. **Teach the Process**: Explain your debugging reasoning
4. **Root Cause**: Help identify the underlying issue, not just symptoms
5. **Prevent Future Issues**: Suggest best practices to avoid similar problems
6. **Don't Give Solutions**: Guide them to find the fix themselves

Format your response with:
- Problem analysis questions
- Debugging strategy
- Guided investigation steps
- Conceptual explanations
- Prevention tips
- Testing recommendations"""

    @staticmethod
    def get_exam_prep_prompt() -> str:
        """Prompt for exam preparation and review mode."""
        return """Mode: EXAM PREPARATION

You are in exam prep mode. Your goal is to help students prepare effectively for assessments.

Guidelines:
1. **Identify Key Topics**: Focus on core concepts most likely to appear
2. **Active Recall**: Use questions and practice problems
3. **Identify Weaknesses**: Help pinpoint areas needing more study
4. **Study Strategies**: Suggest effective study techniques
5. **Test-Taking Tips**: Provide strategies for different question types
6. **Build Confidence**: Reduce anxiety through preparation

Format your response with:
- Key topics to review
- Practice questions
- Study strategy recommendations
- Areas needing focus
- Test-taking strategies
- Time management tips"""

    @staticmethod
    def get_socratic_prompt() -> str:
        """Prompt for Socratic method (questioning) mode."""
        return """Mode: SOCRATIC QUESTIONING

You are in Socratic mode. Your goal is to guide learning through thoughtful questions.

Guidelines:
1. **Ask Open Questions**: Use questions that require thinking, not just recall
2. **Build on Responses**: Follow up based on the student's answers
3. **Challenge Assumptions**: Gently question unstated assumptions
4. **Encourage Reasoning**: Ask "why" and "how" questions
5. **Guide Discovery**: Lead students to discover answers themselves
6. **Be Patient**: Allow time for thinking and exploration

Format your response with:
- Thought-provoking questions
- Follow-up questions based on likely answers
- Hints if they're stuck
- Gentle guidance toward insights
- Validation of good reasoning"""


class IntentClassifier:
    """Classifies student intent to route to appropriate mentor mode."""

    # Keywords for each intent category
    INTENT_KEYWORDS = {
        MentorMode.TUTOR: [
            "teach me", "how do i", "can you explain", "i don't understand",
            "walk me through", "show me how", "help me learn"
        ],
        MentorMode.EXPLAINER: [
            "what is", "what does", "explain", "definition", "meaning",
            "why does", "how does", "clarify"
        ],
        MentorMode.MOTIVATOR: [
            "struggling", "difficult", "frustrated", "give up", "hard",
            "motivation", "discouraged", "stuck", "can't do"
        ],
        MentorMode.DEBUGGER: [
            "error", "bug", "not working", "wrong", "issue", "problem",
            "fix", "debug", "broken", "doesn't work"
        ],
        MentorMode.EXAM_PREP: [
            "exam", "test", "quiz", "prepare", "study", "review",
            "assessment", "practice", "upcoming"
        ],
        MentorMode.SOCRATIC: [
            "why", "think about", "reasoning", "understand why",
            "make me think", "challenge me"
        ]
    }

    @classmethod
    def classify_intent(cls, message: str, context: Dict[str, Any] = None) -> MentorMode:
        """
        Classify student's intent from their message.

        Args:
            message: The student's question/message
            context: Additional context (progress, recent quiz scores, etc.)

        Returns:
            MentorMode enum value
        """
        message_lower = message.lower()

        # Check for explicit mode requests
        if "motivate me" in message_lower or "encourage" in message_lower:
            return MentorMode.MOTIVATOR

        # Score each mode based on keyword matches
        scores = {mode: 0 for mode in MentorMode}

        for mode, keywords in cls.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[mode] += 1

        # Context-based adjustments
        if context:
            # If student is struggling (low quiz scores), bias toward motivator
            if context.get("recent_quiz_score", 100) < 50:
                scores[MentorMode.MOTIVATOR] += 2

            # If in a coding lesson, bias toward debugger
            if context.get("lesson_type") == "CODE":
                scores[MentorMode.DEBUGGER] += 1

        # Get mode with highest score
        max_score = max(scores.values())

        if max_score > 0:
            return max(scores, key=scores.get)

        # Default to general mode
        return MentorMode.GENERAL


class MentorService:
    """
    Enhanced AI mentor service with advanced prompt handling.
    """

    def __init__(self):
        """Initialize the Anthropic client."""
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not configured - AI mentor will not function")
            self.client = None
            return

        self.client = Anthropic(api_key=api_key)
        self.model = settings.AI_MENTOR_MODEL
        self.max_tokens = settings.AI_MENTOR_MAX_TOKENS
        self.temperature = settings.AI_MENTOR_TEMPERATURE

    def build_system_prompt(self, mode: MentorMode = MentorMode.GENERAL) -> str:
        """
        Build system prompt for the specified mentor mode.

        Args:
            mode: The mentor mode to use

        Returns:
            Complete system prompt string
        """
        base = PromptTemplates.get_base_system_prompt()

        mode_prompts = {
            MentorMode.TUTOR: PromptTemplates.get_tutor_prompt(),
            MentorMode.EXPLAINER: PromptTemplates.get_explainer_prompt(),
            MentorMode.MOTIVATOR: PromptTemplates.get_motivator_prompt(),
            MentorMode.DEBUGGER: PromptTemplates.get_debugger_prompt(),
            MentorMode.EXAM_PREP: PromptTemplates.get_exam_prep_prompt(),
            MentorMode.SOCRATIC: PromptTemplates.get_socratic_prompt(),
        }

        mode_prompt = mode_prompts.get(mode, "")

        return f"{base}\n\n{'='*60}\n\n{mode_prompt}"

    def build_context(
        self,
        student,
        course=None,
        lesson=None,
        session_messages: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Build comprehensive context data for the AI mentor.

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
                "name": student.get_full_name() or student.username,
            }
        }

        # Add student profile data
        if hasattr(student, 'student_profile'):
            profile = student.student_profile
            context["student"].update({
                "institution": profile.institution or "Not specified",
                "year_of_study": profile.year_of_study,
                "branch": profile.branch or "Not specified",
                "interests": profile.interests or [],
                "learning_goals": profile.learning_goals or "Not specified",
                "learning_style": profile.preferred_learning_style or "mixed",
                "level": profile.level,
                "total_points": profile.total_points,
            })

        # Add course context
        if course:
            from apps.progress.models import Enrollment

            context["course"] = {
                "title": course.title,
                "difficulty": course.difficulty_level,
                "description": course.short_description or course.description[:200],
            }

            # Add enrollment and progress data
            try:
                enrollment = Enrollment.objects.get(student=student, course=course)
                context["progress"] = {
                    "completion_percentage": float(enrollment.progress_percentage),
                    "status": enrollment.status,
                    "enrolled_days_ago": (enrollment.enrolled_at.date() - student.date_joined.date()).days if hasattr(student, 'date_joined') else 0,
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
                "description": lesson.description or "",
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
                    "time_spent_minutes": progress.time_spent_seconds // 60,
                }
            except LessonProgress.DoesNotExist:
                context["current_lesson"]["progress"] = {"started": False}

        # Add recent quiz performance
        try:
            from apps.assessments.models import QuizAttempt
            recent_attempts = QuizAttempt.objects.filter(
                student=student
            ).order_by('-completed_at')[:3]

            if recent_attempts:
                context["quiz_history"] = [
                    {
                        "quiz": attempt.quiz.title,
                        "score": float(attempt.score),
                        "passed": attempt.passed,
                    }
                    for attempt in recent_attempts
                ]
        except Exception:
            pass

        # Add learning streak data
        try:
            if hasattr(student, 'learning_streak'):
                streak = student.learning_streak
                context["streak"] = {
                    "current_days": streak.current_streak_days,
                    "longest_days": streak.longest_streak_days,
                }
        except Exception:
            pass

        return context

    def format_context_for_prompt(self, context: Dict[str, Any], mode: MentorMode) -> str:
        """
        Format context into a rich, readable prompt segment.

        Args:
            context: Context dictionary
            mode: Current mentor mode

        Returns:
            Formatted context string
        """
        lines = ["<student_context>"]

        # Student info
        student = context.get("student", {})
        lines.append(f"Student Name: {student.get('name', 'Unknown')}")

        if student.get("branch"):
            lines.append(f"Field of Study: {student.get('branch')}")

        if student.get("year_of_study"):
            lines.append(f"Year: {student.get('year_of_study')}")

        if student.get("learning_style"):
            lines.append(f"Preferred Learning Style: {student.get('learning_style')}")

        if student.get("learning_goals"):
            lines.append(f"Learning Goals: {student.get('learning_goals')}")

        if student.get("level"):
            lines.append(f"Current Level: {student.get('level')} (Points: {student.get('total_points', 0)})")

        # Course and progress info
        if "course" in context:
            lines.append("\n<course_info>")
            course = context["course"]
            lines.append(f"Course: {course.get('title')}")
            lines.append(f"Difficulty: {course.get('difficulty')}")

            progress = context.get("progress", {})
            if progress.get("enrolled", True):
                completion = progress.get('completion_percentage', 0)
                lines.append(f"Course Progress: {completion:.1f}%")

                if completion < 25:
                    lines.append("Stage: Just getting started")
                elif completion < 50:
                    lines.append("Stage: Making good progress")
                elif completion < 75:
                    lines.append("Stage: More than halfway there!")
                elif completion < 100:
                    lines.append("Stage: Almost finished!")

                if "current_lesson" in progress:
                    curr = progress["current_lesson"]
                    lines.append(f"Currently On: {curr.get('module')} → {curr.get('title')}")
            lines.append("</course_info>")

        # Current lesson details
        if "current_lesson" in context:
            lines.append("\n<current_lesson>")
            lesson = context["current_lesson"]
            lines.append(f"Lesson: {lesson.get('title')}")
            lines.append(f"Module: {lesson.get('module')}")
            lines.append(f"Content Type: {lesson.get('content_type')}")

            if lesson.get("description"):
                lines.append(f"Description: {lesson.get('description')}")

            lp = lesson.get("progress", {})
            if lp.get("started"):
                lines.append(f"Lesson Progress: {lp.get('completion_percentage', 0):.1f}%")
                lines.append(f"Time Spent: {lp.get('time_spent_minutes', 0)} minutes")
            else:
                lines.append("Status: Not yet started")
            lines.append("</current_lesson>")

        # Quiz history (important for exam prep mode)
        if "quiz_history" in context and mode in [MentorMode.EXAM_PREP, MentorMode.MOTIVATOR]:
            lines.append("\n<quiz_history>")
            for quiz in context["quiz_history"]:
                status = "✓ Passed" if quiz["passed"] else "✗ Needs improvement"
                lines.append(f"- {quiz['quiz']}: {quiz['score']:.1f}% {status}")
            lines.append("</quiz_history>")

        # Learning streak (for motivator mode)
        if "streak" in context and mode == MentorMode.MOTIVATOR:
            lines.append("\n<learning_streak>")
            streak = context["streak"]
            lines.append(f"Current Streak: {streak['current_days']} days")
            lines.append(f"Longest Streak: {streak['longest_days']} days")
            lines.append("</learning_streak>")

        lines.append("</student_context>")
        return "\n".join(lines)

    def ask_mentor(
        self,
        student,
        message: str,
        course=None,
        lesson=None,
        session_messages: Optional[List[Dict]] = None,
        mode: Optional[MentorMode] = None
    ) -> Dict[str, Any]:
        """
        Send a question to the AI mentor with advanced prompt handling.

        Args:
            student: User object (student)
            message: Student's question/message
            course: Course object (optional)
            lesson: Lesson object (optional)
            session_messages: Previous messages in the session (optional)
            mode: Explicit mentor mode (optional, auto-detected if None)

        Returns:
            Dict with mentor response and metadata
        """
        if not self.client:
            return {
                "content": "I apologize, but the AI mentor is not configured. Please contact your administrator.",
                "context": {},
                "model": self.model,
                "tokens_used": 0,
                "suggested_actions": [],
                "mode": "error",
                "error": "ANTHROPIC_API_KEY not configured"
            }

        try:
            # Build context
            context = self.build_context(student, course, lesson, session_messages)

            # Auto-detect mode if not provided
            if mode is None:
                mode = IntentClassifier.classify_intent(message, context)

            logger.info(f"AI Mentor mode selected: {mode.value} for student {student.username}")

            # Build system prompt for this mode
            system_prompt = self.build_system_prompt(mode)

            # Format context
            context_str = self.format_context_for_prompt(context, mode)

            # Build conversation messages
            messages = []

            # Add conversation history if available (last 10 messages for context)
            if session_messages:
                for msg in session_messages[-10:]:
                    messages.append({
                        "role": "user" if msg["role"] == "student" else "assistant",
                        "content": msg["content"]
                    })

            # Add current message with context
            user_message = f"{context_str}\n\n<student_question>\n{message}\n</student_question>"

            messages.append({
                "role": "user",
                "content": user_message
            })

            # Call Claude API
            logger.info(f"Calling Claude API in {mode.value} mode")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )

            # Extract response
            assistant_message = response.content[0].text

            # Parse structured output
            parsed_response = self._parse_response(assistant_message, mode)

            result = {
                "content": assistant_message,
                "context": context,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "suggested_actions": parsed_response.get("actions", []),
                "mode": mode.value,
                "next_steps": parsed_response.get("next_steps", []),
            }

            logger.info(f"Mentor response generated: {result['tokens_used']} tokens, mode={mode.value}")
            return result

        except AnthropicError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return self._error_response(
                "I'm having trouble connecting right now. Please try again in a moment.",
                str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in ask_mentor: {str(e)}", exc_info=True)
            return self._error_response(
                "I encountered an unexpected error. Please contact support if this persists.",
                str(e)
            )

    def _parse_response(self, response_text: str, mode: MentorMode) -> Dict[str, List[str]]:
        """
        Parse AI response to extract structured information.

        Args:
            response_text: The AI's response text
            mode: The mentor mode used

        Returns:
            Dict with parsed actions and suggestions
        """
        parsed = {
            "actions": [],
            "next_steps": [],
        }

        # Extract action suggestions
        action_patterns = [
            r"(?:try|consider|I suggest|you should|recommend) (review(?:ing)? .*?)(?:\.|,|\n)",
            r"(?:try|consider|I suggest|you should|recommend) (practic(?:e|ing) .*?)(?:\.|,|\n)",
            r"(?:try|consider|I suggest|you should|recommend) ((?:take|complete|attempt) .*?)(?:\.|,|\n)",
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            parsed["actions"].extend(matches[:3])  # Limit to top 3

        # Extract next steps if mentioned
        next_step_patterns = [
            r"next step[s]?:?\s*(.*?)(?:\n\n|\Z)",
            r"I recommend:?\s*(.*?)(?:\n\n|\Z)",
        ]

        for pattern in next_step_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
            if matches:
                # Split by newlines or bullet points
                steps = re.split(r'\n[-•*]|\n\d+\.', matches[0])
                parsed["next_steps"].extend([s.strip() for s in steps if s.strip()])

        return parsed

    def _error_response(self, message: str, error: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "content": message,
            "context": {},
            "model": self.model,
            "tokens_used": 0,
            "suggested_actions": [],
            "mode": "error",
            "error": error
        }


# Singleton instance
_mentor_service = None


def get_mentor_service() -> MentorService:
    """Get or create the mentor service singleton."""
    global _mentor_service
    if _mentor_service is None:
        _mentor_service = MentorService()
    return _mentor_service
