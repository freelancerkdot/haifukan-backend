# Haifukan Backend - Authentication System

Django REST Framework backend with custom user authentication, JWT tokens, and email-based registration flow.

## Features

- Custom User model with email-based authentication
- User Profile with role-based access (client, distributor, author, manager)
- Email verification for registration
- JWT token authentication with refresh tokens
- Token blacklist for secure logout
- CORS support for frontend integration

## Setup Instructions

### 1. Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `EMAIL_HOST_USER`: Your Gmail address
- `EMAIL_HOST_PASSWORD`: Gmail app-specific password (generate from Google Account settings)
- `FRONTEND_URL`: Your frontend URL (default: http://localhost:3000)

**Important:** For Gmail, you need to generate an app-specific password:
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new password
4. Use this password in `EMAIL_HOST_PASSWORD`

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication Endpoints

#### 1. Send Verification Email
**POST** `/api/auth/send-verification-email/`

Request body:
```json
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "認証メールを送信しました"
}
```

This creates a user with `is_active=False` and sends a verification email with a token.

#### 2. Verify Token
**POST** `/api/auth/verify-token/`

Request body:
```json
{
  "token": "verification_token_from_email"
}
```

Response:
```json
{
  "message": "トークンが有効です",
  "email": "user@example.com"
}
```

#### 3. Complete Registration
**POST** `/api/auth/complete-registration/?token=verification_token`

Request body:
```json
{
  "role": "client",
  "company_name": "Company Name",
  "full_name": "Full Name",
  "postal_code": "123-4567",
  "address": "Full Address",
  "phone_number": "090-1234-5678",
  "invitation_code": "optional-code",
  "agreed_to_terms": true,
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

Role options:
- `client` - 依頼者
- `distributor` - 配布者
- `author` - 著者
- `manager` - 管理者

Response:
```json
{
  "message": "登録が完了しました"
}
```

This activates the user and creates the UserProfile.

#### 4. Login
**POST** `/api/auth/login/`

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": "user_uuid",
    "user": {
      "id": "user_uuid",
      "email": "user@example.com",
      "username": "username",
      "is_email_verified": true
    },
    "role": "client",
    "company_name": "Company Name",
    "full_name": "Full Name",
    "postal_code": "123-4567",
    "address": "Full Address",
    "phone_number": "090-1234-5678",
    "invitation_code": "optional-code",
    "agreed_to_terms": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 5. Get Profile
**GET** `/api/auth/profile/`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": "profile_uuid",
  "user": {
    "id": "user_uuid",
    "email": "user@example.com",
    "username": "username",
    "is_email_verified": true
  },
  "role": "client",
  "company_name": "Company Name",
  "full_name": "Full Name",
  "postal_code": "123-4567",
  "address": "Full Address",
  "phone_number": "090-1234-5678",
  "invitation_code": "optional-code",
  "agreed_to_terms": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 6. Logout
**POST** `/api/auth/logout/`

Headers:
```
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "refresh": "jwt_refresh_token"
}
```

Response:
```json
{
  "message": "ログアウトしました"
}
```

## Frontend Integration

### Registration Flow

1. **Step 1:** User enters email on `/register` page
2. **Step 2:** Frontend calls `POST /api/auth/send-verification-email/`
3. **Step 3:** User receives email with verification link
4. **Step 4:** User clicks link → redirects to `/confirm?token=xyz`
5. **Step 5:** Frontend calls `POST /api/auth/verify-token/` to validate token
6. **Step 6:** User fills registration form on `/confirm` page
7. **Step 7:** Frontend calls `POST /api/auth/complete-registration/?token=xyz` with form data
8. **Step 8:** User can now login

### Login Flow

1. User enters email and password on `/login` page
2. Frontend calls `POST /api/auth/login/`
3. Store access and refresh tokens (e.g., in localStorage or cookies)
4. Use access token in Authorization header for authenticated requests
5. When access token expires, use refresh token to get new access token
6. Call `POST /api/auth/logout/` with refresh token on logout

### JWT Token Usage

Include the access token in the Authorization header for authenticated requests:

```
Authorization: Bearer <access_token>
```

Access token lifetime: 60 minutes
Refresh token lifetime: 7 days

## Database Models

### User Model
- `id`: UUID (primary key)
- `email`: EmailField (unique, used as username)
- `username`: CharField
- `is_email_verified`: BooleanField
- `email_verification_token`: CharField
- `is_active`: BooleanField
- `created_at`: DateTimeField
- `updated_at`: DateTimeField

### UserProfile Model
- `id`: UUID (primary key)
- `user`: OneToOneField to User
- `role`: CharField (choices: client, distributor, author, manager)
- `company_name`: CharField (optional)
- `full_name`: CharField
- `postal_code`: CharField
- `address`: TextField
- `phone_number`: CharField
- `invitation_code`: CharField (optional)
- `agreed_to_terms`: BooleanField
- `created_at`: DateTimeField
- `updated_at`: DateTimeField

## Admin Panel

Access the admin panel at `http://localhost:8000/admin/`

You can manage users and profiles through the admin interface.

## Security Notes

- JWT tokens are configured with rotation and blacklist for enhanced security
- Email verification tokens are single-use
- Users cannot login until email is verified
- CORS is configured to allow requests from the frontend
- In production, set `DEBUG=False` and use a strong `SECRET_KEY`

## Troubleshooting

### Email not sending
- Verify Gmail app-specific password is correct
- Check that `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set in `.env`
- Ensure 2-Step Verification is enabled on your Google Account

### CORS errors
- Verify `FRONTEND_URL` in `.env` matches your frontend URL
- Check that CORS_ALLOWED_ORIGINS in settings.py includes your frontend URL

### Migration errors
- Delete the database file (`db.sqlite3`) and run migrations again
- Ensure you've renamed the auth app to users (already done in this setup)
