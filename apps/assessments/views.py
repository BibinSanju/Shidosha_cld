"""
Views for the assessments app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Quiz, QuizAttempt, Question, QuestionResponse, Answer
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuizAttemptSerializer,
    SubmitAnswerSerializer,
)


class QuizViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quizzes.
    """
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'module', 'lesson']

    def get_queryset(self):
        queryset = Quiz.objects.all()

        # Filter by course/module/lesson if provided
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # Only show published quizzes to non-staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return QuizDetailSerializer

    @action(detail=True, methods=['post'])
    def start_attempt(self, request, pk=None):
        """Start a new quiz attempt."""
        quiz = self.get_object()
        student = request.user

        # Check max attempts
        if quiz.max_attempts:
            attempt_count = QuizAttempt.objects.filter(
                quiz=quiz,
                student=student
            ).count()

            if attempt_count >= quiz.max_attempts:
                return Response(
                    {'detail': f'Maximum {quiz.max_attempts} attempts reached.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create new attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            status=QuizAttempt.Status.IN_PROGRESS,
            points_possible=quiz.total_points
        )

        return Response({
            'detail': 'Quiz attempt started.',
            'attempt': QuizAttemptSerializer(attempt).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_attempts(self, request):
        """Get all quiz attempts for the current user."""
        attempts = QuizAttempt.objects.filter(student=request.user)
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quiz attempts.
    """
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own attempts
        if self.request.user.is_staff:
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(student=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit an answer to a question in this attempt."""
        attempt = self.get_object()

        # Check if attempt is still in progress
        if attempt.status != QuizAttempt.Status.IN_PROGRESS:
            return Response(
                {'detail': 'Quiz attempt is not in progress.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = serializer.validated_data['question_id']
        selected_answer_id = serializer.validated_data.get('selected_answer_id')
        text_answer = serializer.validated_data.get('text_answer', '')

        # Get question
        question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)

        # Create or update response
        response_data = {
            'attempt': attempt,
            'question': question,
        }

        if selected_answer_id:
            answer = get_object_or_404(Answer, id=selected_answer_id, question=question)
            response_data['selected_answer'] = answer

        if text_answer:
            response_data['text_answer'] = text_answer

        response, created = QuestionResponse.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults=response_data
        )

        return Response({
            'detail': 'Answer submitted successfully.',
            'is_correct': response.is_correct if question.question_type in ['MC', 'TF'] else None
        })

    @action(detail=True, methods=['post'])
    def submit_quiz(self, request, pk=None):
        """Submit the quiz attempt for grading."""
        attempt = self.get_object()

        # Check if attempt is still in progress
        if attempt.status != QuizAttempt.Status.IN_PROGRESS:
            return Response(
                {'detail': 'Quiz attempt is not in progress.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Submit and grade
        attempt.submit()

        return Response({
            'detail': 'Quiz submitted successfully.',
            'attempt': QuizAttemptSerializer(attempt).data
        })

    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        """Get in-progress attempts for the current user."""
        attempts = QuizAttempt.objects.filter(
            student=request.user,
            status=QuizAttempt.Status.IN_PROGRESS
        )
        serializer = self.get_serializer(attempts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed attempts for the current user."""
        attempts = QuizAttempt.objects.filter(
            student=request.user,
            status=QuizAttempt.Status.SUBMITTED
        )
        serializer = self.get_serializer(attempts, many=True)
        return Response(serializer.data)
