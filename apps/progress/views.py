"""
Views for the progress app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Enrollment, LessonProgress, LearningStreak
from .serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    LearningStreakSerializer,
)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for course enrollments.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'course']

    def get_queryset(self):
        # Students can only see their own enrollments
        if self.request.user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=self.request.user)

    @action(detail=False, methods=['get'])
    def my_enrollments(self, request):
        """Get all enrollments for the current user."""
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active enrollments for the current user."""
        enrollments = Enrollment.objects.filter(
            student=request.user,
            status=Enrollment.Status.ACTIVE
        )
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed enrollments for the current user."""
        enrollments = Enrollment.objects.filter(
            student=request.user,
            status=Enrollment.Status.COMPLETED
        )
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def recalculate_progress(self, request, pk=None):
        """Recalculate progress for an enrollment."""
        enrollment = self.get_object()
        progress = enrollment.calculate_progress()
        return Response({
            'detail': 'Progress recalculated.',
            'progress_percentage': progress
        })


class LessonProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lesson progress.
    """
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson', 'is_completed']

    def get_queryset(self):
        # Students can only see their own progress
        if self.request.user.is_staff:
            return LessonProgress.objects.all()
        return LessonProgress.objects.filter(student=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create or update lesson progress."""
        lesson_id = request.data.get('lesson')
        student = request.user

        # Get or create progress
        progress, created = LessonProgress.objects.get_or_create(
            student=student,
            lesson_id=lesson_id,
            defaults=request.data
        )

        if not created:
            # Update existing progress
            serializer = self.get_serializer(progress, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.get_serializer(progress)

        # Update streak
        streak, _ = LearningStreak.objects.get_or_create(student=student)
        streak.update_streak()

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark a lesson as completed."""
        progress = self.get_object()
        progress.mark_complete()

        # Update streak
        streak, _ = LearningStreak.objects.get_or_create(student=request.user)
        streak.update_streak()

        return Response({
            'detail': 'Lesson marked as complete.',
            'progress': LessonProgressSerializer(progress).data
        })

    @action(detail=False, methods=['get'])
    def course_progress(self, request):
        """Get progress for all lessons in a course."""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {'detail': 'course_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress_records = LessonProgress.objects.filter(
            student=request.user,
            lesson__module__course_id=course_id
        )

        serializer = self.get_serializer(progress_records, many=True)
        return Response(serializer.data)


class LearningStreakViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for learning streaks (read-only).
    """
    queryset = LearningStreak.objects.all()
    serializer_class = LearningStreakSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own streak
        if self.request.user.is_staff:
            return LearningStreak.objects.all()
        return LearningStreak.objects.filter(student=self.request.user)

    @action(detail=False, methods=['get'])
    def my_streak(self, request):
        """Get the current user's learning streak."""
        streak, _ = LearningStreak.objects.get_or_create(student=request.user)
        serializer = self.get_serializer(streak)
        return Response(serializer.data)
