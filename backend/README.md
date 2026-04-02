# SSME Backend API

A Django REST API for the Small and Medium-sized Enterprises (SSME) marketplace platform.

## Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Business Management**: Complete CRUD operations for businesses
- **Review System**: Customer reviews and ratings for businesses
- **Category Management**: Organized business categories
- **File Uploads**: Support for business logos and product images
- **Admin Panel**: Django admin for content management
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## User Roles

- **Customer**: Browse businesses, create reviews, manage favorites
- **Business Owner**: Manage business listings, products, and images
- **Administrator**: Full platform management and approval workflows

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- pip and virtualenv
- Git

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ssme/backend

# Create and activate virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration

# Create database and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed the database with sample data
python seed.py

# Start the development server
python manage.py runserver
```

### 3. Environment Variables

Edit `.env` file with the following variables:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-django-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# File Upload
MEDIA_ROOT=media
MEDIA_URL=/media/
MAX_FILE_SIZE=5242880

# CORS
FRONTEND_URL=http://localhost:5173
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout

### Categories

- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create category (admin only)
- `GET /api/categories/<id>/` - Get category details
- `PATCH /api/categories/<id>/` - Update category (admin only)
- `DELETE /api/categories/<id>/` - Delete category (admin only)
- `GET /api/categories/popular/` - Get popular categories

### Businesses

- `GET /api/businesses/` - List businesses (with filtering)
- `POST /api/businesses/` - Create business (business owners only)
- `GET /api/businesses/<id>/` - Get business details
- `PATCH /api/businesses/<id>/` - Update business (owner only)
- `DELETE /api/businesses/<id>/` - Delete business (owner only)
- `GET /api/businesses/featured/` - Get featured businesses
- `GET /api/businesses/<id>/images/` - List business images
- `POST /api/businesses/<id>/images/` - Add business image
- `GET /api/businesses/<id>/products/` - List business products
- `POST /api/businesses/<id>/products/` - Add product

### Favorites

- `GET /api/businesses/favorites/` - List user favorites
- `POST /api/businesses/favorites/` - Add to favorites
- `DELETE /api/businesses/favorites/<id>/` - Remove from favorites

### Reviews

- `GET /api/reviews/` - List reviews (with filtering)
- `POST /api/reviews/` - Create review (customers only)
- `GET /api/reviews/<id>/` - Get review details
- `PATCH /api/reviews/<id>/` - Update review (owner only)
- `DELETE /api/reviews/<id>/` - Delete review (owner only)
- `GET /api/reviews/business/<id>/` - Get business reviews
- `GET /api/reviews/user/` - Get user reviews

## API Documentation

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Use the superuser credentials created during setup.

## Sample Data

The seed script creates the following test accounts:

- **Admin**: admin@ssme.com / admin123
- **Business 1**: business1@ssme.com / business123
- **Business 2**: business2@ssme.com / business123
- **Customer 1**: customer1@ssme.com / customer123
- **Customer 2**: customer2@ssme.com / customer123

## Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── seed.py
├── ssme_backend/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── businesses/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── categories/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── reviews/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
└── media/
    ├── business_logos/
    ├── business_images/
    └── product_images/
```

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure a production database (PostgreSQL recommended)
3. Set up proper `SECRET_KEY`
4. Configure static file serving
5. Set up HTTPS
6. Configure email settings for notifications

## Security Features

- JWT-based authentication with refresh tokens
- Role-based access control
- CORS protection
- File upload validation
- SQL injection protection (Django ORM)
- XSS protection (Django templates)

## License

MIT License
