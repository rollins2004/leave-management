"""
Custom JWT authentication that loads user data from MongoDB
instead of Django's ORM. Works with Python 3.13+.
"""
import jwt
import os
from datetime import datetime, timedelta, timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .db_mongo import users_col
from bson import ObjectId


def make_token_pair(user_doc):
    """Generate access + refresh JWT tokens for a MongoDB user."""
    secret = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me')
    now = datetime.now(timezone.utc)

    access_payload = {
        'user_id': str(user_doc['_id']),
        'username': user_doc['username'],
        'role': user_doc.get('role', 'employee'),
        'exp': now + timedelta(days=1),
        'iat': now,
        'type': 'access',
    }
    refresh_payload = {
        'user_id': str(user_doc['_id']),
        'exp': now + timedelta(days=7),
        'iat': now,
        'type': 'refresh',
    }

    access = jwt.encode(access_payload, secret, algorithm='HS256')
    refresh = jwt.encode(refresh_payload, secret, algorithm='HS256')
    return access, refresh


def decode_access_token(token):
    secret = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        if payload.get('type') != 'access':
            raise AuthenticationFailed('Invalid token type.')
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Access token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')


def decode_refresh_token(token):
    secret = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            raise AuthenticationFailed('Invalid token type.')
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Refresh token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')


class MongoUser:
    """A lightweight user object (not a Django model) built from MongoDB doc."""
    def __init__(self, doc):
        self.id = str(doc['_id'])
        self.username = doc['username']
        self.email = doc.get('email', '')
        self.first_name = doc.get('first_name', '')
        self.last_name = doc.get('last_name', '')
        self.role = doc.get('role', 'employee')
        self.is_authenticated = True
        self.is_anonymous = False

    @property
    def is_employer(self):
        return self.role == 'employer'

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.username

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
        }


class MongoJWTAuthentication(BaseAuthentication):
    """DRF authentication backend that validates JWT and loads user from MongoDB."""

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()
        payload = decode_access_token(token)

        user_id = payload.get('user_id')
        try:
            doc = users_col().find_one({'_id': ObjectId(user_id)})
        except Exception:
            raise AuthenticationFailed('User not found.')

        if not doc:
            raise AuthenticationFailed('User not found.')

        return (MongoUser(doc), token)
