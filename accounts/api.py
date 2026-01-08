from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from .models import User
from .schemas import RegisterSchema, LoginSchema, UserSchema, TokenSchema, MessageSchema
from .jwt_utils import generate_access_token, generate_refresh_token, decode_token
from .auth import JWTAuth

router = Router()


@router.post("/register", response={201: TokenSchema, 400: MessageSchema})
def register(request, payload: RegisterSchema):
    """Register a new user and return JWT tokens"""

    # Check if user already exists
    if User.objects.filter(email=payload.email).exists():
        return 400, {"message": "User with this email already exists"}

    try:
        # Create user
        user = User.objects.create_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number
        )

        # Generate tokens
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        return 201, {
            "access": access_token,
            "refresh": refresh_token
        }
    except Exception as e:
        return 400, {"message": f"Error creating user: {str(e)}"}


@router.post("/login", response={200: TokenSchema, 401: MessageSchema})
def login(request, payload: LoginSchema):
    """Login user and return JWT tokens"""

    user = authenticate(email=payload.email, password=payload.password)

    if user is None:
        return 401, {"message": "Invalid email or password"}

    if not user.is_active:
        return 401, {"message": "User account is disabled"}

    # Generate tokens
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    return 200, {
        "access": access_token,
        "refresh": refresh_token
    }


@router.post("/refresh", response={200: TokenSchema, 400: MessageSchema})
def refresh_token(request, refresh_token: str):
    """Refresh access token"""

    try:
        payload = decode_token(refresh_token)

        if payload.get('type') != 'refresh':
            return 400, {"message": "Invalid token type"}

        user = User.objects.filter(id=payload.get('user_id')).first()

        if not user or not user.is_active:
            return 400, {"message": "User not found or inactive"}

        # Generate new tokens
        new_access_token = generate_access_token(user)
        new_refresh_token = generate_refresh_token(user)

        return 200, {
            "access": new_access_token,
            "refresh": new_refresh_token
        }
    except Exception as e:
        return 400, {"message": "Invalid or expired refresh token"}


@router.get("/me", response=UserSchema, auth=JWTAuth())
def get_current_user(request):
    """Get current authenticated user details"""

    return request.auth
