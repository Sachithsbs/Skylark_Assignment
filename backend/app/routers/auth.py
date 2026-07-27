from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.schemas import Token, LoginRequest, RegisterRequest, UserInfo, UserResponse
from app.utils.security import authenticate_user, create_access_token, get_current_user, get_password_hash
from app.database import get_db, User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT access token."""
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    # Check username is not taken
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken. Please choose a different one.",
        )

    # Enforce minimum password length
    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    hashed_pwd = get_password_hash(req.password)
    new_user = User(
        username=req.username,
        hashed_password=hashed_pwd,
        full_name=req.full_name or "",
        email=req.email or "",
        role="viewer",   # new accounts get viewer role; promote to founder manually
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/me", response_model=UserInfo)
def read_users_me(current_user: UserInfo = Depends(get_current_user)):
    """Return info about the currently authenticated user."""
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all registered users (founder role only)."""
    if current_user.role != "founder":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Founders only")
    return db.query(User).all()
