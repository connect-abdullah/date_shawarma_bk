from app.db.base import Base

# Import all models so they are registered with Base.metadata (for Alembic and relationships)
from app.entities.user.model import User
from app.entities.category.model import Category
from app.entities.product.model import Product
from app.entities.order.model import Order
from app.entities.order_item.model import OrderItem
from app.entities.review.model import Review
from app.entities.complaint_box.model import ComplaintBox
