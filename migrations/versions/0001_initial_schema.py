"""Create initial application schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )

    op.create_table(
        "verbal_autopsy",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patientid", sa.String(length=100), nullable=False),
        sa.Column("state_name", sa.String(length=100), nullable=True),
        sa.Column("lga_name", sa.String(length=100), nullable=True),
        sa.Column("facility_name", sa.String(length=100), nullable=True),
        sa.Column("datim_code", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("sex", sa.String(length=50), nullable=True),
        sa.Column("cause_of_death", sa.String(length=200), nullable=True),
        sa.Column("cause_list", sa.Integer(), nullable=True),
        sa.Column("icd10", sa.String(length=50), nullable=True),
        sa.Column("interviewer_name", sa.String(length=200), nullable=True),
        sa.Column("interview_year", sa.Integer(), nullable=True),
        sa.Column("interview_month", sa.String(length=100), nullable=True),
        sa.Column("interview_day", sa.Integer(), nullable=True),
        sa.Column("interview_time", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patientid"),
    )


def downgrade():
    op.drop_table("verbal_autopsy")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
