<div align="center">

<img src="./screenshots/illustration.png" alt="Job Interview" width="300" height="356.5">

# Birhan Bank VMS (Vacancy Management System)

</div>

## Features

- Job posting and management
- Resume builder with PDF generation
- User authentication (local + social)
- REST API with JWT authentication
- GraphQL support
- Advanced search functionality
- Rate limiting
- Security features (CSRF, XSS protection)
- Employer and Employee dashboards
- Application tracking system
- PDF resume generation

## Prerequisites

- Python 3.8+
- wkhtmltopdf (for PDF generation)
- PostgreSQL (optional, SQLite configured for development)

## Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd Birhan_Bank_VMS
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Install System Dependencies**

- Download and install wkhtmltopdf:
  - Visit <https://wkhtmltopdf.org/downloads.html>
  - Download Windows installer (64-bit)
  - Install and add to PATH during installation

5. **Create required directories**

```bash
mkdir static mediafiles
mkdir mediafiles\resumes
mkdir mediafiles\templates
```

6. **Environment Setup**

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
DJANGO_SETTINGS_MODULE=jobs.settings.local
ELASTIC_HOST_NAME=localhost
ELASTIC_HOST_PORT=9200
ENABLE_PROMETHEUS=False

# Social Auth (optional)
SOCIAL_AUTH_GITHUB_KEY=your-github-key
SOCIAL_AUTH_GITHUB_SECRET=your-github-secret
SOCIAL_AUTH_FACEBOOK_KEY=your-facebook-key
SOCIAL_AUTH_FACEBOOK_SECRET=your-facebook-secret
```

7. **Initialize the Database**

```bash
python manage.py migrate
```

8. **Create a superuser**

```bash
python manage.py createsuperuser
```

9. **Run the development server**

```bash
python manage.py runserver
```

The application will be available at <http://127.0.0.1:8000/>

## Project Structure

```
Birhan_Bank_VMS/
├── accounts/          # User authentication and profiles
├── jobsapp/          # Core job posting and management
├── resume_cv/        # Resume builder functionality
├── tags/            # Job tagging system
├── static/          # Static files
├── mediafiles/      # User uploaded files
└── templates/       # HTML templates
```

## Dependencies

The project uses the following major packages:

```txt
# Core dependencies
Django==5.1.2
djangorestframework==3.15.2
django-cors-headers==4.4.0
django-environ==0.11.2
django-oauth-toolkit==3.0.1
djangorestframework-simplejwt==5.3.1
django-rest-framework-social-oauth2==1.2.0
django-prometheus==2.3.1
django-ratelimit==4.1.0

# Database
psycopg2-binary==2.9.9

# Authentication and OAuth
PyJWT==2.9.0
social-auth-app-django==5.4.2

# PDF Generation
pdfkit==1.0.0

# And more... (see requirements.txt for complete list)
```

## Optional Components

1. **Elasticsearch Setup** (for advanced search)

   - Download and install Elasticsearch
   - Configure in settings
   - Run Elasticsearch service

2. **Redis Setup** (for caching)

   - Download and install Redis
   - Configure in settings

3. **Email Configuration** (for production)
   - Configure SMTP settings in settings.py

## API Documentation

- REST API documentation available at `/api/swagger`
- GraphQL interface available at `/graphql`

## Security Features

- CSRF protection
- XSS protection through content sanitization
- Rate limiting
- JWT authentication
- Secure password hashing
- Input validation and sanitization

## Development

For development work:

```bash
# Install development dependencies
pip install black==24.10.0 pre-commit==4.0.1 isort==5.13.2

# Set up pre-commit hooks
pre-commit install
```

## Production Deployment

Additional steps for production:

1. Set DEBUG=False in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up proper email backend
4. Configure static files serving
5. Set up proper web server (Gunicorn + Nginx recommended)
6. Configure SSL/TLS
7. Set up proper caching

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines]

## Support

[Your Support Information]
