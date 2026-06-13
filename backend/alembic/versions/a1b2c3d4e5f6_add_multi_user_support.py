"""add multi-user support

Revision ID: a1b2c3d4e5f6
Revises: 0a9b19810d4e
Create Date: 2026-06-13 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "0a9b19810d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("pin_hash", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    conn = op.get_bind()
    conn.execute(sa.text("INSERT INTO users (id, name) VALUES (1, 'Default')"))

    tables = ["beans", "grinders", "machines", "shots", "preferences"]
    for table in tables:
        with op.batch_alter_table(table) as batch_op:
            batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))

    for table in tables:
        conn.execute(sa.text(f"UPDATE {table} SET user_id = 1"))

    for table in tables:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column("user_id", nullable=False)
            batch_op.create_foreign_key(
                f"fk_{table}_user_id", "users", ["user_id"], ["id"]
            )

    # Update bean unique constraint to include user_id
    with op.batch_alter_table("beans") as batch_op:
        batch_op.drop_constraint("uq_bean_identity", type_="unique")
        batch_op.create_unique_constraint(
            "uq_bean_identity", ["user_id", "brand", "product"]
        )

    # Add unique constraint on preferences.user_id (one preference row per user)
    with op.batch_alter_table("preferences") as batch_op:
        batch_op.create_unique_constraint("uq_preference_user", ["user_id"])


def downgrade() -> None:
    for table in ["beans", "grinders", "machines", "shots", "preferences"]:
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_constraint(f"fk_{table}_user_id", type_="foreignkey")
            batch_op.drop_column("user_id")

    with op.batch_alter_table("beans") as batch_op:
        batch_op.create_unique_constraint("uq_bean_identity", ["brand", "product"])

    op.drop_table("users")
