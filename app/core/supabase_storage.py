"""
Supabase Storage helper: upload files and get public URLs.

Requires SUPABASE_URL and SUPABASE_KEY (service_role) in .env.
- Create a bucket named "menu" in Supabase Dashboard → Storage, set it to Public.
- If uploads return 403 "row-level security": add an INSERT policy. In Dashboard:
  Storage → menu bucket → Policies → "New policy" → "For full customization":
  - Policy name: Allow menu uploads
  - Allowed operation: INSERT
  - Target roles: check "service_role" (or "authenticated" if using JWT)
  - WITH CHECK expression: (bucket_id = 'menu')
  Or run in SQL Editor:
    create policy "Allow menu uploads" on storage.objects for insert
    with check (bucket_id = 'menu');
"""

from pathlib import Path
from typing import Optional

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Default bucket for menu images; must exist and be public in Supabase
MENU_BUCKET = "menu"

CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def _client():
    """Lazy Supabase client; returns None if not configured."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        logger.warning(f"Supabase client init failed: {e}")
        return None


def upload_menu_image(
    local_path: Path,
    storage_path: str,
    bucket: str = MENU_BUCKET,
    product_name: Optional[str] = None,
) -> Optional[str]:
    """
    Upload a file to Supabase Storage and return its public URL.
    The storage_path should be unique per product (e.g. category/product_slug.ext)
    so the uploaded image is tied to the correct product.

    Args:
        local_path: Path to the local image file (from this product's "image" in menu.json).
        storage_path: Path inside the bucket, must identify this product (e.g. "pizzas/date_special_pizza.jpg").
        bucket: Storage bucket name (default: "menu").
        product_name: Optional; used in logs to confirm which product this image belongs to.

    Returns:
        Public URL of the uploaded file, or None if upload fails or Supabase not configured.
    """
    client = _client()
    if not client:
        logger.warning("Supabase not configured (SUPABASE_URL/SUPABASE_KEY); skip upload.")
        return None

    if not local_path.exists():
        logger.warning(f"Local file not found: {local_path}")
        return None

    try:
        content_type = CONTENT_TYPES.get(local_path.suffix.lower(), "application/octet-stream")
        with open(local_path, "rb") as f:
            client.storage.from_(bucket).upload(
                path=storage_path,
                file=f,
                file_options={"content-type": content_type},
            )
        url = client.storage.from_(bucket).get_public_url(storage_path)
        who = f" for product '{product_name}'" if product_name else ""
        logger.info(f"Uploaded {local_path.name} -> {storage_path}{who} -> {url}")
        return url
    except Exception as e:
        err_str = str(e).lower()
        if "403" in err_str or "row-level security" in err_str or "rls" in err_str:
            logger.error(
                f"Upload failed for {local_path}: {e}. "
                "Fix: Supabase Dashboard → Storage → bucket '%s' → Policies → add policy allowing INSERT (upload). "
                "Use service_role key (SUPABASE_KEY) and ensure a policy allows uploads.",
                bucket,
            )
        else:
            logger.error(f"Upload failed for {local_path}: {e}")
        return None
