"""
Serializers for the assessments app.
"""
from rest_framework import serializers
from .models import Quiz, Question, Answer, QuizAttempt, QuestionResponse


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for quiz answers."""

    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'order']
        # Don't expose is_correct to students!


class AnswerDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz answers with correct flag (for instructors/after submission)."""

    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for quiz questions."""
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'points',
            'order', 'answers'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz questions with explanations (shown after submission)."""
    answers = AnswerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'explanation',
            'points', 'order', 'answers'
        ]


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for quiz list view."""
    course_title = serializers.CharField(source='course.title', read_only=True)
    total_questions = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'course_title',
            'time_limit_minutes', 'passing_score_percentage',
            'total_questions', 'created_at'
        ]


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz detail view."""
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'module', 'lesson',
            'time_limit_minutes', 'passing_score_percentage', 'max_attempts',
            'shuffle_questions', 'shuffle_answers', 'total_questions',
            'total_points', 'questions', 'created_at', 'updated_at'
        ]


class QuestionResponseSerializer(serializers.ModelSerializer):
    """Serializer for question responses."""

    class Meta:
        model = QuestionResponse
        fields = [
            'id', 'question', 'selected_answer', 'text_answer',
            'is_correct', 'points_earned'
        ]
        read_only_fields = ['id', 'is_correct', 'points_earned']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    responses = QuestionResponseSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'status', 'score',
            'points_earned', 'points_possible', 'time_taken_seconds',
            'passed', 'started_at', 'completed_at', 'responses'
        ]
        read_only_fields = [
            'id', 'score', 'points_earned', 'points_possible',
            'passed', 'started_at', 'completed_at'
        ]


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting an answer to a question."""
    question_id = serializers.IntegerField(required=True)
    selected_answer_id = serializers.IntegerField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_blank=True)
