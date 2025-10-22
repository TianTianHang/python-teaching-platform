# Python Teaching Platform

## Project Overview

This is a Python teaching platform that implements a comprehensive system for learning Python programming. The system includes courses, chapters, algorithmic problems, and a code execution service that integrates with the Judge0 API for code evaluation.

### Architecture

The platform is built with a Django backend and React frontend:

- **Backend**: Django REST Framework API with models for Course, Chapter, Problem, AlgorithmProblem, TestCase, and Submission
- **Frontend**: React application in the `web-student` directory for the student interface
- **Code Execution**: Integration with Judge0 API for executing student code submissions against test cases

### Key Components

1. **Models**:
   - `Course`: Represents a course with chapters
   - `Chapter`: Represents a chapter within a course
   - `Problem`: Base model for problems (with different types)
   - `AlgorithmProblem`: Specialized model for algorithmic problems with time/memory limits
   - `TestCase`: Test cases with input and expected output for problems
   - `Submission`: Records of user code submissions and their evaluation results

2. **Services**:
   - `Judge0API`: Wrapper for the Judge0 API to execute code
   - `CodeExecutorService`: Handles the logic for executing code against test cases and managing submission status

3. **API Endpoints**:
   - RESTful endpoints for Course, Chapter, Problem, and Submission entities
   - Special handling for AlgorithmProblem and TestCase relationships

## Building and Running

### Backend Setup
```bash
# Navigate to backend directory
cd backend/

# Initialize the project (if needed)
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/web-student/

# Install dependencies
npm install

# Run the development server
npm start
```

### Environment Variables
The Judge0 API integration requires the following environment variable:
- `RAPIER_API_KEY`: Your Judge0 API key for code execution

## Key Features

1. **Course Structure**: Organized learning paths with courses containing multiple chapters
2. **Algorithm Problems**: Code challenges with automated testing against multiple test cases
3. **Code Execution**: Real-time code execution and evaluation via Judge0 API
4. **Submission Tracking**: Comprehensive tracking of user submissions with status, execution time, memory usage, output, and errors

## Development Conventions

- Python 3.13+ is required
- The codebase follows standard Django and Django REST Framework patterns
- API endpoints are versioned under `/api/v1/`
- Model relationships use appropriate foreign key constraints and nested serializers
- Code execution follows safety practices with time and memory limits

## Special Implementation Details

- The system only allows submissions for problems of type 'algorithm'
- Code execution is handled asynchronously with proper status tracking
- Test cases can be marked as 'sample' for student reference
- The platform includes proper error handling for various execution outcomes