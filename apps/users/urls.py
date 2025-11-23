"""
URL configuration for users app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserViewSet,
    StudentProfileViewSet,
    InstructorProfileViewSet,
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'students', StudentProfileViewSet, basename='student-profile')
router.register(r'instructors', InstructorProfileViewSet, basename='instructor-profile')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
]
