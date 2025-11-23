"""
Views for the lessons app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lesson, LessonAttachment, LessonNote
from .serializers import (
    LessonListSerializer,
    LessonDetailSerializer,
    LessonAttachmentSerializer,
    LessonNoteSerializer,
)


class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lessons.
    """
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['module', 'content_type', 'is_published']

    def get_queryset(self):
        queryset = Lesson.objects.all()

        # Filter by module slug if provided
        module_id = self.request.query_params.get('module_id')
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        # Only show published lessons to non-staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)

        return queryset.order_by('module', 'order')

    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        return LessonDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_complete(self, request, pk=None):
        """
        Mark a lesson as completed for the current user.
        Creates or updates a LessonProgress record.
        """
        from apps.progress.models import LessonProgress

        lesson = self.get_object()
        user = request.user

        # Get or create lesson progress
        progress, created = LessonProgress.objects.get_or_create(
            student=user,
            lesson=lesson,
            defaults={'is_completed': True, 'completion_percentage': 100}
        )

        if not created:
            progress.is_completed = True
            progress.completion_percentage = 100
            progress.save()

        # Award points if student profile exists
        if hasattr(user, 'student_profile'):
            from django.conf import settings
            points = settings.SHIDOSHA_SETTINGS.get('POINTS_PER_LESSON', 10)
            user.student_profile.add_points(points)

        return Response({
            'detail': 'Lesson marked as complete.',
            'points_earned': points if hasattr(user, 'student_profile') else 0
        })

    @action(detail=True, methods=['get'])
    def attachments(self, request, pk=None):
        """Get all attachments for a lesson."""
        lesson = self.get_object()
        attachments = lesson.attachments.all()
        serializer = LessonAttachmentSerializer(
            attachments,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class LessonNoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for student lesson notes.
    """
    queryset = LessonNote.objects.all()
    serializer_class = LessonNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson']

    def get_queryset(self):
        # Students can only see their own notes
        return LessonNote.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
