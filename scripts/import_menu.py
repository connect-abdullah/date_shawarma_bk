#!/usr/bin/env python3
"""
Import menu.json into the database.

Creates categories, products, and product variants from menu.json.

Usage:
    python scripts/import_menu.py
    # or from Docker:
    docker compose exec app python scripts/import_menu.py
"""

import json
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.entities.category.model import Category
from app.entities.category.service import CategoryService
from app.entities.product.model import Product
from app.entities.product_variant.model import ProductVariant
from app.core.logging import get_logger

logger = get_logger(__name__)


def capitalize_category_name(name: str) -> str:
    """Convert 'pizzas' -> 'Pizzas', 'shawarma' -> 'Shawarma', etc."""
    return name.capitalize()


def import_menu(menu_path: str = "menu.json", clear_existing: bool = False):
    """
    Import menu.json into database.

    Args:
        menu_path: Path to menu.json file
        clear_existing: If True, deactivate existing products/variants before importing
    """
    db = SessionLocal()
    try:
        # Load menu.json
        menu_file = Path(__file__).parent.parent / menu_path
        if not menu_file.exists():
            logger.error(f"Menu file not found: {menu_file}")
            return

        with open(menu_file, "r", encoding="utf-8") as f:
            menu_data = json.load(f)

        logger.info(f"Loaded menu.json with {len(menu_data)} categories")

        # Clear existing if requested
        if clear_existing:
            logger.info("Deactivating existing products and variants...")
            db.query(ProductVariant).update({"is_active": False})
            db.query(Product).update({"is_active": False})
            db.commit()

        category_map = {}  # category_name -> category_id

        # Process each category
        for category_key, products in menu_data.items():
            category_name = capitalize_category_name(category_key)

            # Find or create category
            category = db.query(Category).filter(
                Category.category_name == category_name,
                Category.is_active == True
            ).first()

            if not category:
                logger.info(f"Creating category: {category_name}")
                category = Category(
                    category_name=category_name,
                    photo=None,  # Can add pictures later
                )
                db.add(category)
                db.commit()
                db.refresh(category)
            else:
                logger.info(f"Using existing category: {category_name}")

            category_map[category_key] = category.id

            # Process products in this category
            for product_data in products:
                product_name = product_data["name"]
                description = product_data.get("description", "")
                short_description = product_data.get("short_description", "")
                image = product_data.get("image", "")

                # Find or create product
                product = db.query(Product).filter(
                    Product.name == product_name,
                    Product.category_id == category.id,
                    Product.is_active == True
                ).first()

                if not product:
                    logger.info(f"  Creating product: {product_name}")
                    product = Product(
                        name=product_name,
                        description=description,
                        short_description=short_description,
                        category_id=category.id,
                        price=None,  # Price comes from variants
                        photo=image,
                        is_featured=False,
                        is_trending=False,
                        is_available=True,
                    )
                    db.add(product)
                    db.commit()
                    db.refresh(product)
                else:
                    logger.info(f"  Using existing product: {product_name}")
                    # Update product details
                    product.description = description
                    product.short_description = short_description
                    product.photo = image
                    db.commit()

                # Process variants
                variants = product_data.get("variants", [])
                for variant_data in variants:
                    variant_name = variant_data["size"]  # e.g., "Small", "Medium", "5 pieces"
                    variant_price = Decimal(str(variant_data["price"]))

                    # Find or create variant
                    variant = db.query(ProductVariant).filter(
                        ProductVariant.product_id == product.id,
                        ProductVariant.variant_name == variant_name,
                        ProductVariant.is_active == True
                    ).first()

                    if not variant:
                        logger.info(f"    Creating variant: {variant_name} - {variant_price}")
                        variant = ProductVariant(
                            product_id=product.id,
                            variant_name=variant_name,
                            price=variant_price,
                        )
                        db.add(variant)
                    else:
                        logger.info(f"    Updating variant: {variant_name} - {variant_price}")
                        variant.price = variant_price
                        variant.is_active = True

                db.commit()

        logger.info("✅ Menu import completed successfully!")
        logger.info(f"Categories: {len(category_map)}")
        
        # Count totals
        total_products = db.query(Product).filter(Product.is_active == True).count()
        total_variants = db.query(ProductVariant).filter(ProductVariant.is_active == True).count()
        logger.info(f"Products: {total_products}")
        logger.info(f"Variants: {total_variants}")

    except Exception as e:
        logger.error(f"Error importing menu: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import menu.json into database")
    parser.add_argument(
        "--file",
        default="menu.json",
        help="Path to menu.json file (default: menu.json)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Deactivate existing products/variants before importing",
    )
    args = parser.parse_args()

    import_menu(menu_path=args.file, clear_existing=args.clear)
