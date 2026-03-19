import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from functools import wraps
import azure.functions as func

# Get from environment variables or Azure Key Vault
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id: str, email: str, role: str) -> str:
    """Generate a JWT token for a user."""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def require_auth(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(req: func.HttpRequest, *args, **kwargs):
        auth_header = req.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return func.HttpResponse(
                '{"error": "Missing or invalid authorization header"}',
                status_code=401,
                mimetype='application/json'
            )

        token = auth_header.split(' ')[1]
        try:
            payload = decode_token(token)
            req.user = payload  # Attach user info to request
            return f(req, *args, **kwargs)
        except Exception as e:
            return func.HttpResponse(
                f'{{"error": "{str(e)}"}}',
                status_code=401,
                mimetype='application/json'
            )

    return decorated_function
