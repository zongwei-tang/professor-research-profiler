"""actually drop analyses unique constraint

Revision ID: 6b5e3b62db5d
Revises: b2f3c913aa05
Create Date: 2026-07-14 22:06:27.531404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b5e3b62db5d'
down_revision: Union[str, Sequence[str], None] = 'b2f3c913aa05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLAlchemy reflects this table's UNIQUE(...) as a constraint with name=None
    # (confirmed via inspector.get_unique_constraints()), so batch_op.drop_constraint()
    # can't reference it by the sqlite_autoindex_* name. Rebuild the table manually instead.
    op.execute("PRAGMA foreign_keys=OFF")
    op.execute("""
        CREATE TABLE analyses_new (
            analysis_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            author_name VARCHAR NOT NULL,
            analysis_text VARCHAR NOT NULL,
            time VARCHAR,
            interest VARCHAR NOT NULL,
            language VARCHAR NOT NULL,
            provider VARCHAR NOT NULL,
            create_time DATETIME,
            update_time DATETIME,
            PRIMARY KEY (analysis_id),
            CONSTRAINT fk_analyses_user_id_users FOREIGN KEY(user_id) REFERENCES users (user_id)
        )
    """)
    op.execute("""
        INSERT INTO analyses_new (
            analysis_id, user_id, author_id, author_name, analysis_text,
            time, interest, language, provider, create_time, update_time
        )
        SELECT
            analysis_id, user_id, author_id, author_name, analysis_text,
            time, interest, language, provider, create_time, update_time
        FROM analyses
    """)
    op.execute("DROP TABLE analyses")
    op.execute("ALTER TABLE analyses_new RENAME TO analyses")
    op.execute("PRAGMA foreign_keys=ON")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("PRAGMA foreign_keys=OFF")
    op.execute("""
        CREATE TABLE analyses_new (
            analysis_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            author_name VARCHAR NOT NULL,
            analysis_text VARCHAR NOT NULL,
            time VARCHAR,
            interest VARCHAR NOT NULL,
            language VARCHAR NOT NULL,
            provider VARCHAR NOT NULL,
            create_time DATETIME,
            update_time DATETIME,
            PRIMARY KEY (analysis_id),
            CONSTRAINT fk_analyses_user_id_users FOREIGN KEY(user_id) REFERENCES users (user_id),
            UNIQUE (user_id, author_id, interest, language, provider)
        )
    """)
    op.execute("""
        INSERT INTO analyses_new (
            analysis_id, user_id, author_id, author_name, analysis_text,
            time, interest, language, provider, create_time, update_time
        )
        SELECT
            analysis_id, user_id, author_id, author_name, analysis_text,
            time, interest, language, provider, create_time, update_time
        FROM analyses
    """)
    op.execute("DROP TABLE analyses")
    op.execute("ALTER TABLE analyses_new RENAME TO analyses")
    op.execute("PRAGMA foreign_keys=ON")
