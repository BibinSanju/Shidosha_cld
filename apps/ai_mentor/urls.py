"""
URL configuration for AI mentor app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MentorSessionViewSet, MentorFeedbackViewSet

router = DefaultRouter()
router.register(r'sessions', MentorSessionViewSet, basename='mentor-session')
router.register(r'feedback', MentorFeedbackViewSet, basename='mentor-feedback')

urlpatterns = [
    path('', include(router.urls)),
]
