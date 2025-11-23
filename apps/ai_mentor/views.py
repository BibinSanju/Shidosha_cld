"""
Views for the AI mentor app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import MentorSession, MentorMessage, MentorFeedback
from .serializers import (
    MentorSessionSerializer,
    MentorMessageSerializer,
    AskMentorSerializer,
    MentorFeedbackSerializer,
)
from .services import get_mentor_service, MentorMode


class MentorSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for mentor sessions.
    """
    queryset = MentorSession.objects.all()
    serializer_class = MentorSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own sessions
        if self.request.user.is_staff:
            return MentorSession.objects.all()
        return MentorSession.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Get all sessions for the current user."""
        sessions = MentorSession.objects.filter(student=request.user)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """Get active sessions for the current user."""
        sessions = MentorSession.objects.filter(
            student=request.user,
            is_active=True
        )
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """Mark a session as inactive."""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'detail': 'Session ended successfully.'})

    @action(detail=False, methods=['post'])
    def ask(self, request):
        """
        Ask the AI mentor a question.
        Main endpoint for student-mentor interaction.
        """
        serializer = AskMentorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = request.user
        message_text = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        course_id = serializer.validated_data.get('course_id')
        lesson_id = serializer.validated_data.get('lesson_id')
        mode_str = serializer.validated_data.get('mode')

        # Convert mode string to enum if provided
        mode = None
        if mode_str:
            try:
                mode = MentorMode(mode_str)
            except ValueError:
                pass  # Will auto-detect if invalid mode provided

        # Get or create session
        if session_id:
            session = get_object_or_404(MentorSession, id=session_id, student=student)
        else:
            # Create new session
            from apps.courses.models import Course
            from apps.lessons.models import Lesson

            session_data = {'student': student}
            if course_id:
                session_data['course'] = get_object_or_404(Course, id=course_id)
            if lesson_id:
                session_data['lesson'] = get_object_or_404(Lesson, id=lesson_id)

            session = MentorSession.objects.create(**session_data)

            # Auto-generate title from first message
            session.title = message_text[:50] + ('...' if len(message_text) > 50 else '')
            session.save()

        # Save student message
        student_message = MentorMessage.objects.create(
            session=session,
            role=MentorMessage.Role.STUDENT,
            content=message_text
        )

        # Get conversation history
        previous_messages = list(
            session.messages.filter(
                created_at__lt=student_message.created_at
            ).order_by('created_at').values('role', 'content')
        )

        # Call AI mentor service
        mentor_service = get_mentor_service()

        course = session.course
        lesson = session.lesson

        ai_response = mentor_service.ask_mentor(
            student=student,
            message=message_text,
            course=course,
            lesson=lesson,
            session_messages=previous_messages,
            mode=mode
        )

        # Save AI response
        mentor_message = MentorMessage.objects.create(
            session=session,
            role=MentorMessage.Role.MENTOR,
            content=ai_response['content'],
            context_data=ai_response.get('context', {}),
            model_used=ai_response.get('model', ''),
            tokens_used=ai_response.get('tokens_used', 0),
            suggested_actions=ai_response.get('suggested_actions', [])
        )

        return Response({
            'session_id': session.id,
            'student_message': MentorMessageSerializer(student_message).data,
            'mentor_response': MentorMessageSerializer(mentor_message).data,
            'mode_used': ai_response.get('mode', 'general'),
            'next_steps': ai_response.get('next_steps', []),
        }, status=status.HTTP_201_CREATED)


class MentorFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for mentor feedback.
    """
    queryset = MentorFeedback.objects.all()
    serializer_class = MentorFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own feedback
        if self.request.user.is_staff:
            return MentorFeedback.objects.all()
        return MentorFeedback.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
