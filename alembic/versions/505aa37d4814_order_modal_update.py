"""order modal update

Revision ID: 505aa37d4814
Revises: 00b5596068b3
Create Date: 2026-02-19 19:52:21.471557

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '505aa37d4814'
down_revision = '00b5596068b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the enum type first
    payment_method_enum = postgresql.ENUM(
        'COD', 'BANK_TRANSFER',
        name='paymentmethodenum',
        create_type=True
    )
    payment_method_enum.create(op.get_bind(), checkfirst=True)
    
    # Now add the column using the enum type
    op.add_column(
        'orders',
        sa.Column(
            'payment_method',
            payment_method_enum,
            nullable=False,
            server_default='COD'  # Provide default for existing rows
        )
    )


def downgrade() -> None:
    # Drop the column first
    op.drop_column('orders', 'payment_method')
    
    # Then drop the enum type
    postgresql.ENUM(name='paymentmethodenum').drop(op.get_bind(), checkfirst=True)
