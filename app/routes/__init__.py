from fastapi import APIRouter
from app.routes.user import router as user_router
from app.routes.category import router as category_router
from app.routes.product import router as product_router
from app.routes.order import router as order_router
from app.routes.review import router as review_router
from app.routes.complaint_box import router as complaint_box_router

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(category_router)
router.include_router(product_router)
router.include_router(order_router)
router.include_router(review_router)
router.include_router(complaint_box_router)
