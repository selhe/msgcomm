"""create schema

Revision ID: 202502071200
Revises: 
Create Date: 2025-02-07 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202502071200"
down_revision = None
branch_labels = None
depends_on = None


message_type_enum = sa.Enum(
    "text", "attachment", "system", name="message_type_enum", native_enum=False
)

message_status_enum = sa.Enum(
    "sent", "delivered", "read", name="message_status_enum", native_enum=False
)

conversation_status_enum = sa.Enum(
    "open", "closed", "blocked", name="conversation_status_enum", native_enum=False
)


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("item_id", sa.String(length=255), nullable=False),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("status", conversation_status_enum, nullable=False),
        sa.Column("last_message_id", sa.Integer(), nullable=True),
        sa.Column("last_message_date", sa.DateTime(), nullable=True),
        sa.Column("buyer_unread_count", sa.Integer(), nullable=True),
        sa.Column("seller_unread_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["buyer_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seller_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("type", message_type_enum, nullable=False),
        sa.Column("content", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("status", message_status_enum, nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversation.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sender_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "attachment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("type", message_type_enum, nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["message.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("attachment")
    op.drop_table("message")
    op.drop_table("conversation")
    op.drop_table("user")
