"""
Progress tracking models for Shidosha Learning Platform.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Course
from apps.lessons.models import Lesson


class Enrollment(models.Model):
    """
    Student enrollment in a course.
    Tracks overall course progress and status.
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        DROPPED = 'dropped', _('Dropped')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'}
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Overall course completion percentage (0-100)')
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Date when the course was completed')
    )
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Last time the student accessed this course')
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        ordering = ['-enrolled_at']
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', '-enrolled_at']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})"

    def calculate_progress(self):
        """
        Calculate and update the progress percentage based on completed lessons.
        Formula: (completed_lessons / total_lessons) * 100
        """
        from apps.lessons.models import Lesson

        total_lessons = Lesson.objects.filter(
            module__course=self.course,
            is_published=True
        ).count()

        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                student=self.student,
                lesson__module__course=self.course,
                is_completed=True
            ).count()

            self.progress_percentage = (completed_lessons / total_lessons) * 100

        # Auto-complete course if 100% done
        if self.progress_percentage >= 100 and self.status == self.Status.ACTIVE:
            from django.utils import timezone
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()

            # Award completion points
            if hasattr(self.student, 'student_profile'):
                points = settings.SHIDOSHA_SETTINGS.get('POINTS_PER_COURSE_COMPLETION', 100)
                self.student.student_profile.add_points(points)

        self.save()
        return self.progress_percentage

    @property
    def current_lesson(self):
        """Get the lesson the student should continue from."""
        # Get the first incomplete lesson
        from apps.lessons.models import Lesson

        incomplete_lesson = Lesson.objects.filter(
            module__course=self.course,
            is_published=True
        ).exclude(
            id__in=LessonProgress.objects.filter(
                student=self.student,
                is_completed=True
            ).values_list('lesson_id', flat=True)
        ).order_by('module__order', 'order').first()

        return incomplete_lesson


class LessonProgress(models.Model):
    """
    Tracks student progress for individual lessons.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        limit_choices_to={'role': 'STUDENT'}
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='student_progress'
    )
    is_completed = models.BooleanField(
        default=False,
        help_text=_('Whether the lesson is marked as complete')
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Progress within the lesson (0-100)')
    )
    time_spent_seconds = models.IntegerField(
        default=0,
        help_text=_('Total time spent on this lesson (in seconds)')
    )
    last_position_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Last video position for video lessons')
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Date when the lesson was completed')
    )
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Lesson Progress')
        verbose_name_plural = _('Lesson Progress')
        ordering = ['-last_accessed_at']
        unique_together = ['student', 'lesson']
        indexes = [
            models.Index(fields=['student', 'is_completed']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} ({self.completion_percentage}%)"

    def mark_complete(self):
        """Mark lesson as completed and update enrollment progress."""
        from django.utils import timezone

        if not self.is_completed:
            self.is_completed = True
            self.completion_percentage = 100
            self.completed_at = timezone.now()
            self.save()

            # Update course enrollment progress
            try:
                enrollment = Enrollment.objects.get(
                    student=self.student,
                    course=self.lesson.module.course
                )
                enrollment.calculate_progress()
            except Enrollment.DoesNotExist:
                pass


class LearningStreak(models.Model):
    """
    Tracks student learning streaks for gamification.
    """
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_streak',
        limit_choices_to={'role': 'STUDENT'}
    )
    current_streak_days = models.IntegerField(
        default=0,
        help_text=_('Current consecutive days of learning')
    )
    longest_streak_days = models.IntegerField(
        default=0,
        help_text=_('Longest streak ever achieved')
    )
    last_activity_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Last date of learning activity')
    )
    total_learning_days = models.IntegerField(
        default=0,
        help_text=_('Total number of days with learning activity')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Learning Streak')
        verbose_name_plural = _('Learning Streaks')

    def __str__(self):
        return f"{self.student.username} - {self.current_streak_days} days"

    def update_streak(self):
        """Update the streak based on today's activity."""
        from django.utils import timezone
        today = timezone.now().date()

        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days

            if days_diff == 0:
                # Already updated today
                return
            elif days_diff == 1:
                # Consecutive day
                self.current_streak_days += 1
            else:
                # Streak broken
                self.current_streak_days = 1
        else:
            # First activity
            self.current_streak_days = 1

        # Update longest streak
        if self.current_streak_days > self.longest_streak_days:
            self.longest_streak_days = self.current_streak_days

        self.last_activity_date = today
        self.total_learning_days += 1
        self.save()
