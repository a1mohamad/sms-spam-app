from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import AppConfig



class Database:
    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(
            database_url,
            pool_pre_ping=True,
        )
        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=self._engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False
        )

    def get_session(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        self._engine.dispose()


database = Database(database_url=AppConfig.get_database_url())