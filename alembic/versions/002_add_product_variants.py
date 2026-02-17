"""add product variants table and variant_id to order_items

Revision ID: 002
Revises: 001
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add OUT_FOR_DELIVERY to OrderStatusEnum
    op.execute("ALTER TYPE orderstatusenum ADD VALUE IF NOT EXISTS 'OUT_FOR_DELIVERY'")

    # product_variants table
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("variant_name", sa.String(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_product_variants_id"),
        "product_variants",
        ["id"],
        unique=False,
    )

    # add variant_id to order_items
    op.add_column(
        "order_items",
        sa.Column("variant_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "order_items_variant_id_fkey",
        "order_items",
        "product_variants",
        ["variant_id"],
        ["id"],
    )

    # make products.price nullable (variants hold the prices)
    op.alter_column(
        "products",
        "price",
        existing_type=sa.Numeric(10, 2),
        nullable=True,
    )


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly.
    # To remove OUT_FOR_DELIVERY, you'd need to recreate the enum type.
    # For now, we'll leave it in place.

    # revert products.price nullability
    op.alter_column(
        "products",
        "price",
        existing_type=sa.Numeric(10, 2),
        nullable=False,
    )

    # drop variant_id from order_items
    op.drop_constraint(
        "order_items_variant_id_fkey",
        "order_items",
        type_="foreignkey",
    )
    op.drop_column("order_items", "variant_id")

    # drop product_variants
    op.drop_index(op.f("ix_product_variants_id"), table_name="product_variants")
    op.drop_table("product_variants")

