import jwt
from datetime import datetime, timedelta
from django.conf import settings
from typing import Dict, Any


def generate_access_token(user) -> str:
    """Generate JWT access token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME'],
        'iat': datetime.utcnow(),
        'type': 'access'
    }

    token = jwt.encode(
        payload,
        settings.JWT_SETTINGS['SIGNING_KEY'],
        algorithm=settings.JWT_SETTINGS['ALGORITHM']
    )

    return token


def generate_refresh_token(user) -> str:
    """Generate JWT refresh token for user"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + settings.JWT_SETTINGS['REFRESH_TOKEN_LIFETIME'],
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }

    token = jwt.encode(
        payload,
        settings.JWT_SETTINGS['SIGNING_KEY'],
        algorithm=settings.JWT_SETTINGS['ALGORITHM']
    )

    return token


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SETTINGS['SIGNING_KEY'],
            algorithms=[settings.JWT_SETTINGS['ALGORITHM']]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
