from ninja.security import HttpBearer
from .jwt_utils import decode_token
from .models import User


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = decode_token(token)

            if payload.get('type') != 'access':
                return None

            user = User.objects.filter(id=payload.get('user_id')).first()

            if user and user.is_active:
                return user

            return None
        except Exception:
            return None
