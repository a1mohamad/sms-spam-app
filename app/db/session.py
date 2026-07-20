from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import AppConfig


class Database:
    """Manage the SQLAlchemy engine and database sessions."""

    def __init__(self, database_url: str) -> None:
        """Initialize the database engine and session factory.

        Args:
            database_url: SQLAlchemy-compatible database connection URL.
        """
        self._engine: Engine = create_engine(
            database_url,
            # Detect connections that became invalid while inside the pool.
            pool_pre_ping=True,
            hide_parameters=True,
        )

        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=self._engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
        )

    def get_session(self) -> Generator[Session, None, None]:
        """Provide a database session for one unit of work.

        The session is rolled back when an operation fails and is always closed
        after the caller finishes using it.

        Yields:
            Session: A request-scoped SQLAlchemy session.
        """
        session = self._session_factory()

        try:
            # Commit decisions belong to the service or repository layer.
            yield session
        except Exception:
            # Clear any incomplete transaction before propagating the error.
            session.rollback()
            raise
        finally:
            # Return the connection to SQLAlchemy's connection pool.
            session.close()

    def dispose(self) -> None:
        """Close all connections maintained by the database engine."""
        self._engine.dispose()


# Maintain one engine and connection pool for the application process.
database = Database(
    database_url=AppConfig.get_database_url(),
)