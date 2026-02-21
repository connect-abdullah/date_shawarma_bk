#!/usr/bin/env python3
"""
Import menu.json into the database.

For each product image: uploads the image to Supabase Storage (if local file exists
and Supabase is configured), then saves the product with the Supabase public URL.
Otherwise uses the original image path from JSON.

Expects local images in an `images/` directory (or --images-dir) with filenames
matching menu.json "image" paths, e.g. "/images/special_pizza.jpg" -> images/special_pizza.jpg.

Usage:
    python scripts/import_menu.py
    python scripts/import_menu.py --images-dir ./images --file menu.json
    docker compose exec app python scripts/import_menu.py --images-dir /app/images
"""

import json
import re
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.entities.category.model import Category
from app.entities.product.model import Product
from app.entities.product_variant.model import ProductVariant
from app.core.logging import get_logger
from app.core.supabase_storage import upload_menu_image

logger = get_logger(__name__)


def capitalize_category_name(name: str) -> str:
    """Convert 'pizzas' -> 'Pizzas', 'shawarma' -> 'Shawarma', etc."""
    return name.capitalize()


def slug_for_path(s: str) -> str:
    """Make a safe storage path segment from a name."""
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[-\s]+", "_", s).strip("_").lower() or "item"


def _find_image_file(images_dir: Path, project_root: Path, basename: str) -> Path | None:
    """
    Find image file for a given basename (e.g. special_pizza.jpg from menu.json).
    - Tries exact path, then case-insensitive same name.
    - Then tries same stem with any extension (menu has .jpg but disk has .png).
    """
    base_dir = images_dir if images_dir.is_absolute() else project_root / images_dir
    if not base_dir.is_dir():
        return None

    candidate = base_dir / basename
    if candidate.exists():
        return candidate

    stem = Path(basename).stem.lower()

    for f in base_dir.iterdir():
        if not f.is_file():
            continue
        if f.name.lower() == basename.lower():
            return f
        # Same stem, different extension (e.g. menu: special_pizza.jpg, disk: special_pizza.png)
        if f.stem.lower() == stem:
            return f

    return None


def resolve_photo_url(
    image_value: str,
    category_key: str,
    product_name: str,
    images_dir: Path,
    project_root: Path,
) -> str:
    """
    Upload this product's image to Supabase bucket "menu", get public URL, return it.
    Only the Supabase public URL is returned; we never store paths like /images/... in the DB.
    """
    if not image_value:
        return ""

    basename = Path(image_value).name
    local_path = _find_image_file(images_dir, project_root, basename)

    if local_path is None:
        logger.warning(f"No local file for '{product_name}' (expected {basename}); photo will be empty")
        return ""

    ext = local_path.suffix
    slug = slug_for_path(product_name)
    storage_path = f"{category_key}/{slug}{ext}"
    url = upload_menu_image(local_path, storage_path, product_name=product_name)

    if url:
        logger.info(f"  -> Product '{product_name}' | {local_path.name} -> bucket 'menu'/{storage_path} | URL saved to DB")
        return url

    logger.warning(f"Upload failed for '{product_name}'; SUPABASE_URL/SUPABASE_KEY and bucket 'menu' required. Photo left empty.")
    return ""


def import_menu(
    menu_path: str = "menu.json",
    clear_existing: bool = False,
    images_dir: str = "images",
):
    """
    Import menu.json into database.
    For each product image: upload to Supabase if local file exists, then save product with that URL.
    """
    project_root = Path(__file__).parent.parent
    images_dir_path = Path(images_dir) if Path(images_dir).is_absolute() else project_root / images_dir

    db = SessionLocal()
    try:
        menu_file = project_root / menu_path
        if not menu_file.exists():
            logger.error(f"Menu file not found: {menu_file}")
            return

        with open(menu_file, "r", encoding="utf-8") as f:
            menu_data = json.load(f)

        logger.info(f"Loaded menu.json with {len(menu_data)} categories")
        if images_dir_path.exists():
            logger.info(f"Images directory: {images_dir_path}")
        else:
            logger.warning(f"Images directory not found: {images_dir_path}; will use image paths from JSON as-is.")

        if clear_existing:
            logger.info("Deactivating existing products and variants...")
            db.query(ProductVariant).update({"is_active": False})
            db.query(Product).update({"is_active": False})
            db.commit()

        for category_key, products in menu_data.items():
            category_name = capitalize_category_name(category_key)

            category = db.query(Category).filter(
                Category.category_name == category_name,
                Category.is_active == True,
            ).first()

            if not category:
                logger.info(f"Creating category: {category_name}")
                category = Category(
                    category_name=category_name,
                    photo=None,
                )
                db.add(category)
                db.commit()
                db.refresh(category)
            else:
                logger.info(f"Using existing category: {category_name}")

            for product_data in products:
                product_name = product_data["name"]
                description = product_data.get("description", "")
                short_description = product_data.get("short_description", "")
                # This product's image only: e.g. Date Special Pizza -> "image": "/images/special_pizza.jpg"
                # We use this value only for this product so the right image goes to the right item.
                image_value = product_data.get("image", "")

                # Upload this product's image to Supabase (from image_value); get URL and save to DB for this product only
                photo_url = resolve_photo_url(
                    image_value,
                    category_key,
                    product_name,
                    images_dir_path,
                    project_root,
                )

                product = db.query(Product).filter(
                    Product.name == product_name,
                    Product.category_id == category.id,
                    Product.is_active == True,
                ).first()

                if not product:
                    logger.info(f"  Creating product: {product_name}")
                    product = Product(
                        name=product_name,
                        description=description,
                        short_description=short_description,
                        category_id=category.id,
                        photo=photo_url,
                        is_featured=False,
                        is_trending=False,
                        is_available=True,
                    )
                    db.add(product)
                    db.commit()
                    db.refresh(product)
                else:
                    logger.info(f"  Updating product: {product_name}")
                    product.description = description
                    product.short_description = short_description
                    product.photo = photo_url
                    db.commit()

                for variant_data in product_data.get("variants", []):
                    variant_name = variant_data["size"]
                    variant_price = Decimal(str(variant_data["price"]))

                    variant = db.query(ProductVariant).filter(
                        ProductVariant.product_id == product.id,
                        ProductVariant.variant_name == variant_name,
                        ProductVariant.is_active == True,
                    ).first()

                    if not variant:
                        variant = ProductVariant(
                            product_id=product.id,
                            variant_name=variant_name,
                            price=variant_price,
                        )
                        db.add(variant)
                    else:
                        variant.price = variant_price
                        variant.is_active = True

                db.commit()

        total_products = db.query(Product).filter(Product.is_active == True).count()
        total_variants = db.query(ProductVariant).filter(ProductVariant.is_active == True).count()
        logger.info("✅ Menu import completed successfully!")
        logger.info(f"Categories: {len(menu_data)} | Products: {total_products} | Variants: {total_variants}")

    except Exception as e:
        logger.error(f"Error importing menu: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Import menu.json into database; upload images to Supabase and save product photo URLs."
    )
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
    parser.add_argument(
        "--images-dir",
        default="images",
        help="Directory containing image files (e.g. images/special_pizza.jpg for image path /images/special_pizza.jpg). Default: images",
    )
    args = parser.parse_args()

    import_menu(
        menu_path=args.file,
        clear_existing=args.clear,
        images_dir=args.images_dir,
    )
