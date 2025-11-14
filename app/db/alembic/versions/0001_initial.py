from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('event_type', sa.String, nullable=False),
        sa.Column('channel', sa.String, nullable=False),
        sa.Column('recipient', sa.String, nullable= False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('status', sa.String,  default='pending'),
        sa.Column('attempt', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('notifications')