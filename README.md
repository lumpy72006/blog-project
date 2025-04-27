# Valley Blog Platform

A full-featured blogging platform with authentication, post management, and advanced search capabilities.

## Features

### Core Functionality
- **User Authentication**: Signup, login, and logout
- **Post Management**: 
  - Create, edit, and delete posts
  - Draft vs. published status
  - Reading time estimation
- **Comments**: 
  - Authenticated users can comment
  - Admin-approved comment system

### Advanced Search
- **Search across**:
  - Post titles
  - Content
  - Author names (username)
  - Tags
- **Smart visibility**:
  - Hidden on auth/management pages
  - Only shows published posts

### Engagement Features
- Post likes
- View counters
- Tagging system

## Technical Stack
- **Backend**: Django 5.1
- **Frontend**: 
  - CSS
  - Bootstrap 5
  - Font Awesome 6
- **Database**: SQLite (default)
- **Deployment**: Ready for production (WSGI compatible)

## Installation
```bash
# Clone repository
git clone https://github.com/yourusername/blog-project.git
cd blog-project

# Set up virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Migrate database
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
