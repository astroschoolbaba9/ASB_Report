from fastapi import APIRouter, Depends
from security import dev_or_api_key
from AI.ai_api import router as ai_router
from numerology.num_api import router as numerology_router
from auth.auth_api import router as auth_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(numerology_router, dependencies=[Depends(dev_or_api_key)])
router.include_router(ai_router, dependencies=[Depends(dev_or_api_key)])
