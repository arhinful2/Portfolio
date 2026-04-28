# Deployment Guide

This guide covers deploying the Aarhinful Portfolio application to Vercel with PostgreSQL.

## 📋 Prerequisites

- Vercel account ([vercel.com](https://vercel.com))
- PostgreSQL database (Vercel PostgreSQL or external provider)
- GitHub repository connected to Vercel
- Domain name (optional, Vercel provides free `.vercel.app` domain)

## 🔧 Environment Variables

Set these environment variables in your Vercel project settings:

### Required Variables

| Variable | Description | Example |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key (generate a strong random key) | `your-long-random-secret-key` |
| `DJANGO_DEBUG` | Debug mode (must be False in production) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts (comma-separated) | `yourdomain.com,www.yourdomain.com` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/dbname` |

### Optional Variables

| Variable | Description | Default |
| --- | --- | --- |
| `VERCEL_BLOB_READ_WRITE_TOKEN` | Blob storage token for media files | (empty) |
| `DJANGO_SUPERUSER_USERNAME` | Superuser username for auto-creation | (empty) |
| `DJANGO_SUPERUSER_EMAIL` | Superuser email for auto-creation | (empty) |
| `DJANGO_SUPERUSER_PASSWORD` | Superuser password for auto-creation | (empty) |

## 🚀 Deployment Steps

### Step 1: Prepare Your Code

1. **Ensure all changes are committed**

   ```bash
   git status
   git add .
   git commit -m "Prepare for deployment"
   ```

2. **Verify static files configuration**
   - Static files are configured for Vercel with WhiteNoise
   - No additional setup required

3. **Check for sensitive data**
   ```bash
   # Ensure no credentials are in:
   # - requirements.txt
   # - .env file (should be in .gitignore)
   # - Any source code files
   ```

### Step 2: Configure Vercel Project

1. **Login to Vercel**

   ```bash
   vercel login
   ```

2. **Link your project** (if not already linked)

   ```bash
   vercel link
   ```

3. **Set environment variables**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add all required variables from the table above
   - Ensure variables are set for Production environment

### Step 3: Configure Database

#### Option A: Use Vercel PostgreSQL (Recommended)

1. Navigate to your Vercel project dashboard
2. Go to Storage → Create Database → Postgres
3. Follow the wizard to create the database
4. Vercel will automatically add `DATABASE_URL` to your environment variables
5. Verify the connection string is set

#### Option B: Use External PostgreSQL Provider

1. Get your PostgreSQL connection string from your provider
2. Format: `postgres://username:password@host:5432/database_name`
3. Add as `DATABASE_URL` environment variable in Vercel

### Step 4: Deploy

1. **Deploy from CLI**

   ```bash
   vercel --prod
   ```

2. **Or trigger automatic deployment**
   - Push to your main branch on GitHub
   - Vercel will automatically build and deploy

### Step 5: Run Migrations

After first deployment, run migrations on the production database:

```bash
# Via Vercel CLI
vercel env pull

# Run migrations
python manage.py migrate --noinput

# Create superuser (if not using auto-creation)
python manage.py createsuperuser
```

Or use the Vercel Function approach - Migrations run automatically on first deployment via settings.py

### Step 6: Verify Deployment

1. **Check deployment status**
   - Visit your Vercel project dashboard
   - Verify the latest deployment is marked "Ready"

2. **Test your application**
   - Visit your domain: `https://yourdomain.com`
   - Try accessing `/admin/` with your superuser credentials
   - Test profile page loading
   - Test contact form submission

3. **Check logs**

   ```bash
   vercel logs
   ```

## 📊 Pre-Deployment Checklist

- [ ] Django `DEBUG = False` in production settings
- [ ] `DJANGO_SECRET_KEY` is set to a secure random value
- [ ] `DJANGO_ALLOWED_HOSTS` includes your domain
- [ ] Database `DATABASE_URL` is configured and accessible
- [ ] Static files collection is working
- [ ] No `.env` file is committed to Git (check `.gitignore`)
- [ ] All environment variables are set in Vercel
- [ ] CSRF and security settings are configured
- [ ] Email backend is configured (if using email features)
- [ ] Media storage is configured (Vercel Blob or alternative)

## 🔑 Generating Secret Key

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use Python:

```python
import secrets
print(secrets.token_urlsafe(50))
```

Copy the generated key and add it to Vercel environment variables as `DJANGO_SECRET_KEY`.

## 🗄️ Database Migrations

### Initial Setup

```bash
# Run initial migrations
python manage.py migrate
```

### After Making Model Changes

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Commit and push to trigger redeployment
git add portfolio/migrations/
git commit -m "Add new migrations"
git push
```

## 📁 Media Files

### Using Vercel Blob Storage

The application supports Vercel Blob for media storage:

1. Go to Vercel Dashboard → Storage → Create Store → Blob
2. Copy the token to `VERCEL_BLOB_READ_WRITE_TOKEN`
3. Update `settings.py` to use Blob storage backend

### Using Local Storage

For development and small deployments, use local media folder:

- Media files are stored in `/media/` directory
- Ensure directory permissions are correct
- Back up media files separately for production

## 🛡️ Security Best Practices

1. **Never commit secrets**
   - Use `.gitignore` for `.env` and sensitive files
   - Only store secrets in Vercel environment variables

2. **Use strong secret keys**
   - Generate with Django's `get_random_secret_key()`
   - Rotate periodically

3. **HTTPS enforcement**
   - Vercel provides free HTTPS
   - All traffic is automatically redirected to HTTPS

4. **Regular updates**
   - Keep Django and dependencies updated
   - Monitor security advisories   ```bash
   pip list --outdated
   ```

5. **Database backups**
   - Enable automated backups in your database provider
   - Test restoration periodically

## 🔧 Troubleshooting

### Build Fails

1. **Check build logs**

   ```bash
   vercel logs --follow
   ```

2. **Common issues**
   - Missing environment variables
   - Static files not collected
   - Python version mismatch (use Python 3.11+)

### Database Connection Errors

1. **Verify DATABASE_URL**

   ```bash
   vercel env pull
   ```

2. **Test connection**

   ```python
   python manage.py dbshell
   ```

3. **Check PostgreSQL is accepting connections**
   - Verify IP whitelist allows Vercel IPs

### Static Files Not Loading

1. **Ensure WhiteNoise is installed**

   ```bash
   pip install whitenoise
   ```

2. **Collect static files**

   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Check `STATIC_ROOT` in settings.py**

### Media Files Not Accessible

1. **Verify media storage configuration**
   - Check `MEDIA_URL` and `MEDIA_ROOT` settings
   - Verify Vercel Blob token if using blob storage

2. **Check file permissions**
   - Ensure uploaded files are readable by the application

## 📞 Support & Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)

## 🔄 Continuous Deployment

The project is configured for automatic deployment:

1. **Push to main branch**

   ```bash
   git push origin main
   ```

2. **Vercel automatically**
   - Detects code changes
   - Builds the application
   - Runs tests (if configured)
   - Deploys to production

3. **Monitor deployment**
   - Check Vercel dashboard
   - View real-time logs
   - Rollback if needed

## 📝 Environment-Specific Settings

### Development

- `DEBUG = True`
- SQLite or local PostgreSQL
- Static files served by Django

### Production (Vercel)

- `DEBUG = False`
- PostgreSQL database
- Static files via WhiteNoise
- Media storage via Vercel Blob

---

**Last Updated**: April 2026

For more information about the application structure, see [README.md](README.md).
