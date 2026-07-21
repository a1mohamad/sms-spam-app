from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import AppConfig
from app.core.errors import DatabaseUnavailableError


class Database:
    """Manage the SQLAlchemy engine and database sessions."""

    def __init__(
        self,
        database_url: str,
        connect_timeout_seconds: int = AppConfig.DB_CONNECT_TIMEOUT_SECONDS,
    ) -> None:
        """Initialize the database engine and session factory.

        Args:
            database_url: SQLAlchemy-compatible database connection URL.
            connect_timeout_seconds: Maximum wait for a new PostgreSQL
                connection.
        """
        self._engine: Engine = create_engine(
            database_url,
            # Detect connections that became invalid while inside the pool.
            pool_pre_ping=True,
            # Bound both pool checkout and new network-connection waits so a
            # readiness request cannot hang on an unavailable dependency.
            pool_timeout=connect_timeout_seconds,
            hide_parameters=True,
            connect_args={"connect_timeout": connect_timeout_seconds},
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

    def check_connection(self) -> None:
        """Verify that the database can execute a lightweight query.

        Raises:
            DatabaseUnavailableError: If a connection cannot be established or
                PostgreSQL cannot execute the readiness query.
        """
        try:
            with self._engine.connect() as connection:
                # Execute a real round trip rather than checking only whether
                # SQLAlchemy can hand out a pooled connection object.
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise DatabaseUnavailableError(
                "Database readiness check failed."
            ) from exc


# Maintain one engine and connection pool for the application process.
database = Database(
    database_url=AppConfig.get_database_url(),
    connect_timeout_seconds=AppConfig.DB_CONNECT_TIMEOUT_SECONDS,
)
