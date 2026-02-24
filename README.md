# Valley
<img width="969" height="646" alt="image" src="https://github.com/user-attachments/assets/c372bdb2-5f5f-41f9-955f-5d11a794d3c4" />


A full-featured blogging platform with authentication, post management, and advanced search capabilities.

## Features

### Core Functionality
- **User Authentication**: Signup, login, and logout
 <img width="1101" height="382" alt="image" src="https://github.com/user-attachments/assets/e26bcbdc-1bda-42ec-b9a1-6a68ff153d12" />

- **User Profiles**:
  - View user profiles
  <img width="595" height="341" alt="image" src="https://github.com/user-attachments/assets/1cadc4f0-1576-40c9-81f4-96ef527d12e4" />

  - Edit profile information: bio and profile picture
  <img width="599" height="379" alt="image" src="https://github.com/user-attachments/assets/fa368e8b-9745-4ce2-8cc7-573e09a68a30" />

- **Post Management**: 
  - Create, edit, and delete posts
  - Draft vs. published status
  - Reading time estimation
- **Comments**: 
  - Authenticated users can comment
  - Admin-approved comment system

### Search
- **Search across**:
  - Post titles
  - Content
  - Author names (username)
- **Smart visibility**:
  - Only shows published posts

### Engagement Features
- Post likes
- View counters

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
git clone https://github.com/lumpy72006/blog-project.git
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
