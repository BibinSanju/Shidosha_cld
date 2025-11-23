# Shidosha - AI-Powered Learning Platform

**Shidosha** is an intelligent learning management system that combines traditional course management with an AI-powered mentor to provide personalized, adaptive learning experiences for students.

## 🎯 Key Features

### Learning Management System (LMS)
- **Course Management**: Create and organize courses with modules and lessons
- **Multiple Content Types**: Support for text, video, interactive content, and coding exercises
- **Progress Tracking**: Comprehensive tracking of student progress through courses
- **Assessments**: Built-in quiz system with multiple question types and auto-grading
- **Enrollments**: Easy course enrollment and completion tracking

### AI-Powered Mentor
- **Personalized Guidance**: Context-aware AI mentor using Claude that adapts to each student's:
  - Learning history and progress
  - Current course and lesson context
  - Quiz performance and weak areas
  - Academic profile and goals
- **Intelligent Tutoring**: Step-by-step explanations and concept clarification
- **Actionable Suggestions**: Recommends next steps, review materials, and practice exercises
- **Conversational Sessions**: Maintains conversation context for natural interactions

### Student Experience
- **Gamification**: Points, levels, and achievement tracking to motivate learning
- **Learning Streaks**: Track consecutive days of learning activity
- **Personal Notes**: Take and manage notes within lessons
- **Dashboard**: Comprehensive view of courses, progress, and recommendations

### Instructor Tools
- **Course Builder**: Intuitive course creation with modules and lessons
- **Content Management**: Upload files, videos, and create rich content
- **Assessment Creation**: Build quizzes with various question types
- **Student Analytics**: Track student progress and performance

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Django 5.0 - Web framework
- Django REST Framework - API development
- PostgreSQL / SQLite - Database
- Celery + Redis - Async task processing
- Anthropic Claude API - AI mentor

**Authentication:**
- JWT-based authentication
- Role-based access control (Student, Instructor, Admin)

**APIs:**
- RESTful API design
- Comprehensive filtering and search
- Pagination support

### Project Structure

```
shidosha_platform/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── shidosha/                # Main project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI config
│   ├── asgi.py              # ASGI config
│   └── celery.py            # Celery configuration
├── apps/                    # Django applications
│   ├── users/               # User management & profiles
│   ├── courses/             # Course & module management
│   ├── lessons/             # Lesson content & attachments
│   ├── progress/            # Enrollment & progress tracking
│   ├── ai_mentor/           # AI mentor integration
│   └── assessments/         # Quizzes & grading
└── logs/                    # Application logs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Redis (for Celery task queue)
- PostgreSQL (recommended for production) or SQLite (development)
- Anthropic API key for AI mentor functionality

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Shidosha_cld
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your configuration, especially:
   # - SECRET_KEY (generate a new one for production)
   # - ANTHROPIC_API_KEY (required for AI mentor)
   # - DATABASE_URL (if using PostgreSQL)
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000`

9. **Start Celery worker (optional, in a separate terminal)**
   ```bash
   celery -A shidosha worker --loglevel=info
   ```

### Quick Start - Creating Your First Course

1. **Access the admin panel**: `http://localhost:8000/admin`
2. Log in with your superuser credentials
3. Create a **Category** (e.g., "Computer Science")
4. Create a **Course** with title, description, and category
5. Add **Modules** to organize lessons
6. Create **Lessons** with content
7. Optionally add **Quizzes** for assessment
8. Publish the course by setting `is_published=True`

## 📚 API Documentation

### Authentication

**Register a new user:**
```
POST /api/users/register/
{
  "username": "student1",
  "email": "student@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "STUDENT"
}
```

**Login (get JWT token):**
```
POST /api/auth/token/
{
  "username": "student1",
  "password": "securepassword"
}
```

**Use token in headers:**
```
Authorization: Bearer <access_token>
```

### Key Endpoints

#### Courses
- `GET /api/courses/` - List all published courses
- `GET /api/courses/{slug}/` - Get course details
- `POST /api/courses/{slug}/enroll/` - Enroll in a course
- `GET /api/courses/my_courses/` - Get instructor's courses

#### Lessons
- `GET /api/lessons/?module_id={id}` - Get lessons for a module
- `GET /api/lessons/{id}/` - Get lesson details
- `POST /api/lessons/{id}/mark_complete/` - Mark lesson as complete

#### Progress
- `GET /api/progress/enrollments/my_enrollments/` - Get user's enrollments
- `GET /api/progress/lessons/` - Get lesson progress
- `GET /api/progress/streaks/my_streak/` - Get learning streak

#### AI Mentor
- `POST /api/mentor/sessions/ask/` - Ask the AI mentor a question
```json
{
  "message": "Can you explain variables in Python?",
  "course_id": 1,
  "lesson_id": 5
}
```
- `GET /api/mentor/sessions/my_sessions/` - Get conversation history

#### Assessments
- `GET /api/assessments/quizzes/?course_id={id}` - Get course quizzes
- `POST /api/assessments/quizzes/{id}/start_attempt/` - Start quiz
- `POST /api/assessments/attempts/{id}/submit_answer/` - Submit answer
- `POST /api/assessments/attempts/{id}/submit_quiz/` - Submit quiz

### User Dashboard
```
GET /api/users/me/dashboard_stats/
```
Returns:
- Total enrollments
- Active courses
- Completed courses
- Total points
- Current level

## 🤖 AI Mentor Integration

The AI mentor is powered by Anthropic's Claude and provides:

### Context-Aware Responses
The mentor automatically considers:
- Student profile (year, branch, interests, learning goals)
- Current course and lesson
- Learning progress and completion percentage
- Recent quiz performance
- Conversation history

### Usage Example

```python
# Student asks a question
POST /api/mentor/sessions/ask/
{
  "message": "I'm struggling with recursion. Can you help?",
  "lesson_id": 42
}

# AI Mentor responds with:
# - Step-by-step explanation
# - Examples related to the current lesson
# - Suggestions to review prerequisite material
# - Practice exercises or next lessons to try
```

### Customization

Edit `apps/ai_mentor/services.py` to customize:
- System prompt and mentor personality
- Context building logic
- Response parsing and action extraction
- Model parameters (temperature, max tokens)

## 🎮 Gamification System

### Points
- **Lesson completion**: 10 points (configurable)
- **Quiz completion**: 20 points
- **Course completion**: 100 points

### Levels
- Students level up every 100 points
- Level displayed in profile and leaderboards

### Streaks
- Track consecutive days of learning
- Maintain longest streak records
- Encourage daily engagement

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Critical Settings:**
- `SECRET_KEY`: Django secret key (generate new for production)
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `DATABASE_URL`: Database connection string
- `DEBUG`: Set to `False` in production

**AI Mentor Settings:**
- `AI_MENTOR_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `AI_MENTOR_MAX_TOKENS`: Max tokens per response (default: 2000)
- `AI_MENTOR_TEMPERATURE`: Response creativity (0.0-1.0, default: 0.7)

**Feature Flags:**
- `ENABLE_AI_MENTOR`: Enable/disable AI mentor feature
- `ENABLE_GAMIFICATION`: Enable/disable points and levels

### Shidosha-Specific Settings

In `shidosha/settings.py`, adjust:

```python
SHIDOSHA_SETTINGS = {
    'MIN_LESSON_COMPLETION_PERCENT': 80,
    'QUIZ_PASS_THRESHOLD': 70,
    'POINTS_PER_LESSON': 10,
    'POINTS_PER_QUIZ': 20,
    'POINTS_PER_COURSE_COMPLETION': 100,
}
```

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

Run with coverage:
```bash
pytest --cov=apps
```

## 🚢 Deployment

### Production Checklist

1. **Environment**
   - Set `DEBUG=False`
   - Generate new `SECRET_KEY`
   - Configure production database (PostgreSQL recommended)
   - Set proper `ALLOWED_HOSTS`

2. **Database**
   - Run migrations: `python manage.py migrate`
   - Create superuser: `python manage.py createsuperuser`

3. **Static Files**
   - Collect static files: `python manage.py collectstatic`

4. **Services**
   - Set up Gunicorn/uWSGI for Django
   - Configure Nginx/Apache as reverse proxy
   - Start Redis for Celery
   - Start Celery worker and beat scheduler

5. **Security**
   - Enable HTTPS
   - Configure CORS properly
   - Set up firewall rules
   - Enable security headers (already configured when DEBUG=False)

### Docker Deployment (Coming Soon)

Docker and docker-compose configurations will be added in future updates.

## 📖 Development Guide

### Adding a New App

1. Create the app: `python manage.py startapp app_name`
2. Add to `INSTALLED_APPS` in `settings.py`
3. Create models, serializers, views
4. Add URLs to main `urls.py`
5. Create migrations: `python manage.py makemigrations`
6. Apply migrations: `python manage.py migrate`

### AI Mentor Best Practices

1. **Rich Context**: Always provide course, lesson, and student context
2. **Conversation History**: Include recent messages for continuity
3. **Error Handling**: Handle API failures gracefully with fallbacks
4. **Token Management**: Monitor token usage to control costs
5. **Feedback Loop**: Collect student feedback to improve prompts

### Code Style

- Follow PEP 8 for Python code
- Use Django best practices
- Write docstrings for functions and classes
- Keep views thin, use service layer for business logic
- Write tests for new features

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Built with Django and Django REST Framework
- AI powered by Anthropic's Claude
- Inspired by modern learning platforms and AI-assisted education

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

---

**Shidosha** - Empowering students with AI-guided learning 🚀
