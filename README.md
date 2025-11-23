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
  "lesson_id": 5,
  "mode": "explainer"
}
```
Available modes: `tutor`, `explainer`, `motivator`, `debugger`, `exam_prep`, `socratic`, `general` (auto-detected if not specified)

- `GET /api/mentor/sessions/my_sessions/` - Get conversation history
- `GET /api/mentor/sessions/active_sessions/` - Get active conversation sessions

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

The AI mentor is powered by Anthropic's Claude and provides **7 specialized learning modes** with intelligent prompt routing.

### 🎯 Mentor Modes

The AI mentor automatically adapts to different learning scenarios:

#### 1. **Tutor Mode** (`tutor`)
Step-by-step teaching and guided learning
- Diagnoses current understanding
- Builds concepts incrementally
- Includes comprehension checks
- Provides practice activities
- **Auto-triggered by**: "teach me", "how do i", "walk me through"

#### 2. **Explainer Mode** (`explainer`)
Deep concept explanation and clarification
- Starts with simple definitions (ELI5)
- Adds complexity gradually
- Uses analogies and real-world examples
- Addresses common misconceptions
- **Auto-triggered by**: "what is", "explain", "clarify", "why does"

#### 3. **Motivator Mode** (`motivator`)
Encouragement and emotional support
- Acknowledges struggles and validates feelings
- Celebrates progress and achievements
- Reframes challenges as growth opportunities
- Sets achievable goals
- **Auto-triggered by**: "struggling", "frustrated", "difficult", "give up"
- Also triggered automatically when quiz scores < 50%

#### 4. **Debugger Mode** (`debugger`)
Problem-solving and code debugging
- Asks clarifying questions about the issue
- Guides through systematic debugging
- Teaches the debugging process
- Identifies root causes
- Suggests prevention strategies
- **Auto-triggered by**: "error", "bug", "not working", "broken", "fix"

#### 5. **Exam Prep Mode** (`exam_prep`)
Test preparation and review
- Identifies key topics for review
- Provides practice questions
- Suggests study strategies
- Pinpoints weak areas
- Offers test-taking tips
- **Auto-triggered by**: "exam", "test", "quiz", "prepare", "study"

#### 6. **Socratic Mode** (`socratic`)
Learning through guided questioning
- Asks thought-provoking questions
- Encourages critical thinking
- Challenges assumptions gently
- Guides discovery rather than telling
- **Auto-triggered by**: "why", "make me think", "challenge me"

#### 7. **General Mode** (`general`)
Open-ended guidance and conversation
- Flexible responses to any question
- Adapts to context dynamically
- Default fallback when no specific mode detected

### 🧠 Intelligent Intent Detection

The AI mentor **automatically detects** the best mode based on:
- **Keywords in the question**: Analyzes language patterns
- **Student context**: Recent quiz scores, progress, current lesson type
- **Learning history**: Past interactions and challenges

You can also **explicitly specify** a mode in your request:

```python
POST /api/mentor/sessions/ask/
{
  "message": "I'm having trouble with this recursive function",
  "mode": "debugger",  # Force debugger mode
  "lesson_id": 42
}
```

### 📊 Rich Context-Aware Responses

The mentor automatically considers:
- **Student Profile**: Year, branch, interests, learning goals, preferred learning style
- **Current Course**: Title, difficulty level, description
- **Progress**: Completion percentage, current lesson, time spent
- **Quiz History**: Recent scores and pass/fail status (last 3 attempts)
- **Learning Streak**: Current and longest streaks
- **Conversation History**: Last 10 messages for continuity

### 💡 Usage Examples

#### Example 1: Auto-Detected Explainer Mode
```bash
POST /api/mentor/sessions/ask/
{
  "message": "What is polymorphism in OOP?",
  "course_id": 5
}

# Response includes:
# {
#   "mode_used": "explainer",
#   "mentor_response": {
#     "content": "Let me explain polymorphism starting simple...",
#     "suggested_actions": ["review the inheritance lesson", ...]
#   },
#   "next_steps": [...]
# }
```

#### Example 2: Explicit Socratic Mode
```bash
POST /api/mentor/sessions/ask/
{
  "message": "How should I approach this algorithm problem?",
  "mode": "socratic",
  "lesson_id": 23
}

# AI will respond with guiding questions instead of direct answers
```

#### Example 3: Motivator Mode for Struggling Student
```bash
POST /api/mentor/sessions/ask/
{
  "message": "I'm really struggling with this course",
  "course_id": 3
}

# Auto-detects "struggling" → motivator mode
# Uses quiz history and progress to provide personalized encouragement
```

### 🔧 Advanced Customization

Edit `apps/ai_mentor/services.py` to customize:

**Prompt Templates** (`PromptTemplates` class):
- Modify system prompts for each mode
- Add new mentor modes
- Adjust communication style

**Intent Classification** (`IntentClassifier` class):
- Add new keywords for mode detection
- Adjust scoring weights
- Add context-based routing rules

**Context Building** (`MentorService.build_context`):
- Add new data sources (assignments, peer comparisons, etc.)
- Customize what context is included for each mode

**Response Parsing** (`MentorService._parse_response`):
- Extract structured data from responses
- Identify actionable suggestions
- Parse next steps recommendations

### 🎨 Structured Output

Every mentor response includes:
```python
{
  "content": "The AI's response text (markdown formatted)",
  "mode_used": "tutor",  # Which mode was selected
  "suggested_actions": [
    "review Module 2, Lesson 3",
    "practice coding exercises",
    "take the practice quiz"
  ],
  "next_steps": [
    "Complete the current lesson exercises",
    "Try implementing a simple example",
    ...
  ],
  "tokens_used": 1250,
  "model": "claude-3-5-sonnet-20241022"
}
```

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
