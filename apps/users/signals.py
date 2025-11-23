"""
Signals for the users app.
Automatically create profiles when users are created.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, InstructorProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create appropriate profile when a new user is created."""
    if created:
        if instance.role == User.Role.STUDENT:
            StudentProfile.objects.create(user=instance)
        elif instance.role == User.Role.INSTRUCTOR:
            InstructorProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved."""
    if instance.role == User.Role.STUDENT and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == User.Role.INSTRUCTOR and hasattr(instance, 'instructor_profile'):
        instance.instructor_profile.save()
