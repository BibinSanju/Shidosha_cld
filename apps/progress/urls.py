"""
URL configuration for progress app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSet, LessonProgressViewSet, LearningStreakViewSet

router = DefaultRouter()
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'lessons', LessonProgressViewSet, basename='lesson-progress')
router.register(r'streaks', LearningStreakViewSet, basename='learning-streak')

urlpatterns = [
    path('', include(router.urls)),
]
