"""
URL configuration for lessons app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, LessonNoteViewSet

router = DefaultRouter()
router.register(r'', LessonViewSet, basename='lesson')
router.register(r'notes', LessonNoteViewSet, basename='lesson-note')

urlpatterns = [
    path('', include(router.urls)),
]
