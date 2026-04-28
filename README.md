# Aarhinful Portfolio

A modern, feature-rich Django-based portfolio and project showcase application with professional profile management, media gallery, and contact messaging capabilities.

## 🌟 Features

- **Professional Profile Management**: Create and customize a LinkedIn-style portfolio
  - Profile cover image and avatar
  - Customizable theme colors
  - Comprehensive bio and headline
  - Contact information management
  
- **Experience & Education Tracking**: Showcase your professional journey
  - Work experience timeline
  - Education history
  - Skills and endorsements
  
- **Project Portfolio**: Display your best work
  - Project descriptions with rich text editor
  - Media gallery with downloadable files
  - Project completion status tracking
  - Before/after media comparisons

- **Dynamic Content Sections**: Flexible page layout
  - Customizable sections with visibility controls
  - Section ordering and arrangement
  - Rich HTML content support

- **Contact Management**: Built-in contact form
  - Contact form with validation
  - Message storage and replies
  - Admin notification system
  - Auto-reply functionality

- **Admin Dashboard**: Comprehensive management interface
  - Custom admin panels
  - Media upload management
  - System configuration controls
  - SEO settings (meta tags, favicon)

- **Media Management**: Secure file handling
  - User-organized media storage
  - File access controls
  - Download restrictions per file
  - Support for images and documents

## 🛠️ Technology Stack

- **Backend**: Django 6.0
- **Database**: PostgreSQL
- **Frontend**: HTML/CSS/JavaScript with TinyMCE editor
- **Hosting**: Vercel
- **Static Files**: WhiteNoise, Vercel Blob Storage
- **Image Processing**: Pillow

## 📋 Requirements

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## 🚀 Quick Start

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aarhinful2
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your local settings (see DEPLOYMENT.md for variables)

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://localhost:8000` in your browser

## 📁 Project Structure

```
aarhinful2/
├── portfolio/              # Main portfolio app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── migrations/        # Database migrations
├── custom_admin/          # Custom admin enhancements
├── portfolio_core/        # Project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI application
├── templates/             # HTML templates
├── static/                # CSS, JavaScript, images
├── media/                 # User-uploaded files
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## 🔐 Security

- Secret key stored in environment variables
- Debug mode disabled in production
- CSRF protection enabled
- Secure password handling with Django's auth system
- Media file access controls
- SQL injection prevention via Django ORM
- XSS protection with template auto-escaping

## 📝 Configuration

Key settings are configured via environment variables:

- `DJANGO_SECRET_KEY`: Secret key for Django
- `DJANGO_DEBUG`: Debug mode (True/False)
- `DJANGO_ALLOWED_HOSTS`: Allowed hosts (comma-separated)
- `DATABASE_URL`: PostgreSQL connection string
- `VERCEL_BLOB_READ_WRITE_TOKEN`: Blob storage access (for Vercel)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete configuration details.

## 🤝 Admin Panel

Access the Django admin at `/admin/`:
- Manage profile information
- Create and edit projects
- Handle contact messages
- Manage media files
- Configure system settings
- Control section visibility

## 📱 Responsive Design

The portfolio is fully responsive and works seamlessly on:
- Desktop browsers
- Tablets
- Mobile devices

## 📄 License

This project is private and confidential.

## 🐛 Support

For issues or questions, please contact the project maintainer.

---

**Last Updated**: April 2026
