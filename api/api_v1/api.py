from fastapi import APIRouter
from . import auth
from . import profile
from . import friends
from . import users

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
router.include_router(friends.router, prefix="/friends", tags=["friends"])
router.include_router(users.router, prefix="/users", tags=["users"])