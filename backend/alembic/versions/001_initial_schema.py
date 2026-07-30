"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-07-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(), nullable=False),
        sa.Column('prediction', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('probability_up', sa.Float(), nullable=False),
        sa.Column('probability_down', sa.Float(), nullable=False),
        sa.Column('model_used', sa.String(), nullable=False),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_asset'), 'predictions', ['asset'], unique=False)
    op.create_index(op.f('ix_predictions_id'), 'predictions', ['id'], unique=False)
    
    # Create model_performance table
    op.create_table(
        'model_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=False),
        sa.Column('precision', sa.Float(), nullable=False),
        sa.Column('recall', sa.Float(), nullable=False),
        sa.Column('f1_score', sa.Float(), nullable=False),
        sa.Column('roc_auc', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_performance_asset'), 'model_performance', ['asset'], unique=False)
    op.create_index(op.f('ix_model_performance_id'), 'model_performance', ['id'], unique=False)
    op.create_index(op.f('ix_model_performance_model_name'), 'model_performance', ['model_name'], unique=False)
    
    # Create market_data table
    op.create_table(
        'market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('change_24h', sa.Float(), nullable=False),
        sa.Column('volume_24h', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_asset'), 'market_data', ['asset'], unique=False)
    op.create_index(op.f('ix_market_data_id'), 'market_data', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_market_data_id'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_asset'), table_name='market_data')
    op.drop_table('market_data')
    
    op.drop_index(op.f('ix_model_performance_model_name'), table_name='model_performance')
    op.drop_index(op.f('ix_model_performance_id'), table_name='model_performance')
    op.drop_index(op.f('ix_model_performance_asset'), table_name='model_performance')
    op.drop_table('model_performance')
    
    op.drop_index(op.f('ix_predictions_id'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_asset'), table_name='predictions')
    op.drop_table('predictions')
