"""
User models for Shidosha Learning Platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports both students and instructors/staff.
    """
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        INSTRUCTOR = 'INSTRUCTOR', _('Instructor')
        ADMIN = 'ADMIN', _('Admin')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('User role in the platform')
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Must be unique.')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Contact phone number')
    )
    bio = models.TextField(
        blank=True,
        help_text=_('Short biography or introduction')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Profile picture')
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text=_('Date of birth')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR


class StudentProfile(models.Model):
    """
    Extended profile for student users.
    Stores learning preferences, goals, and academic information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': User.Role.STUDENT}
    )
    institution = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('School/College/University name')
    )
    year_of_study = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Current year of study (1, 2, 3, 4, etc.)')
    )
    branch = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Branch/Major/Specialization (e.g., Computer Science)')
    )
    interests = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of learning interests and topics')
    )
    learning_goals = models.TextField(
        blank=True,
        help_text=_('Student learning goals and aspirations')
    )
    preferred_learning_style = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('visual', _('Visual')),
            ('auditory', _('Auditory')),
            ('reading', _('Reading/Writing')),
            ('kinesthetic', _('Kinesthetic')),
            ('mixed', _('Mixed')),
        ],
        default='mixed',
        help_text=_('Preferred learning style')
    )
    total_points = models.IntegerField(
        default=0,
        help_text=_('Total gamification points earned')
    )
    level = models.IntegerField(
        default=1,
        help_text=_('Current level based on points')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')

    def __str__(self):
        return f"Profile: {self.user.get_full_name() or self.user.username}"

    def add_points(self, points):
        """Add points and update level."""
        self.total_points += points
        # Level up every 100 points
        self.level = (self.total_points // 100) + 1
        self.save()


class InstructorProfile(models.Model):
    """
    Extended profile for instructor users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        limit_choices_to={'role': User.Role.INSTRUCTOR}
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Academic/Professional title (e.g., Professor, Dr., etc.)')
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Organization/Institution name')
    )
    expertise = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of expertise areas and subjects')
    )
    website = models.URLField(
        blank=True,
        help_text=_('Personal or professional website')
    )
    linkedin = models.URLField(
        blank=True,
        help_text=_('LinkedIn profile URL')
    )
    verified = models.BooleanField(
        default=False,
        help_text=_('Whether the instructor is verified')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Instructor Profile')
        verbose_name_plural = _('Instructor Profiles')

    def __str__(self):
        return f"Instructor: {self.user.get_full_name() or self.user.username}"
