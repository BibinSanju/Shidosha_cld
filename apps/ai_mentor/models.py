"""
AI Mentor models for Shidosha Learning Platform.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class MentorSession(models.Model):
    """
    A conversation session between a student and the AI mentor.
    Groups related messages together.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_sessions',
        limit_choices_to={'role': 'STUDENT'}
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_sessions',
        help_text=_('Course context for this session')
    )
    lesson = models.ForeignKey(
        'lessons.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_sessions',
        help_text=_('Specific lesson context for this session')
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Session title (auto-generated from first message)')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this session is currently active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Mentor Session')
        verbose_name_plural = _('Mentor Sessions')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['student', '-updated_at']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.title or 'Untitled'} ({self.created_at.strftime('%Y-%m-%d')})"


class MentorMessage(models.Model):
    """
    Individual messages in a mentor conversation.
    Stores both student questions and AI responses.
    """
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        MENTOR = 'mentor', _('AI Mentor')
        SYSTEM = 'system', _('System')

    session = models.ForeignKey(
        MentorSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices
    )
    content = models.TextField(
        help_text=_('Message content')
    )
    # Context information used for the AI response
    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Context used to generate this message (student profile, progress, etc.)')
    )
    # AI model metadata
    model_used = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('AI model name/version used')
    )
    tokens_used = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Number of tokens consumed')
    )
    # Suggested actions from AI
    suggested_actions = models.JSONField(
        default=list,
        blank=True,
        help_text=_('Suggested next steps (e.g., "next_lesson", "review_quiz")')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mentor Message')
        verbose_name_plural = _('Mentor Messages')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class MentorFeedback(models.Model):
    """
    Student feedback on AI mentor responses.
    Used to improve the mentor over time.
    """
    message = models.OneToOneField(
        MentorMessage,
        on_delete=models.CASCADE,
        related_name='feedback',
        limit_choices_to={'role': MentorMessage.Role.MENTOR}
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_feedback'
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text=_('Rating from 1 (poor) to 5 (excellent)')
    )
    comment = models.TextField(
        blank=True,
        help_text=_('Optional feedback comment')
    )
    was_helpful = models.BooleanField(
        default=True,
        help_text=_('Whether the response was helpful')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mentor Feedback')
        verbose_name_plural = _('Mentor Feedback')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - Rating: {self.rating}/5"
