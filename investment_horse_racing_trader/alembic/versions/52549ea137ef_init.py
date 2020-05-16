"""init

Revision ID: 52549ea137ef
Revises:
Create Date: 2020-05-16 07:53:40.862835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52549ea137ef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vote_record",
        sa.Column("vote_record_id", sa.String(255), primary_key=True),
        sa.Column("race_id", sa.String(255), nullable=False),
        sa.Column("bet_type", sa.String(255), nullable=False),
        sa.Column("horse_number_1", sa.Integer, nullable=False),
        sa.Column("horse_number_2", sa.Integer, nullable=True),
        sa.Column("horse_number_3", sa.Integer, nullable=True),
        sa.Column("odds", sa.Float, nullable=False),
        sa.Column("vote_cost", sa.Integer, nullable=False),
        sa.Column("result", sa.Integer, nullable=True),
        sa.Column("result_odds", sa.Float, nullable=True),
        sa.Column("vote_return", sa.Integer, nullable=True),
        sa.Column("vote_parameter", sa.String(4000), nullable=False),
        sa.Column("create_timestamp", sa.DateTime, nullable=False),
        sa.Column("update_timestamp", sa.DateTime, nullable=True),
    )


def downgrade():
    pass
