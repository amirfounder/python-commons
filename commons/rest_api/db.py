from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from commons.logging import log_warning
from commons.rest_api.base_model import Base


def drop_schema(engine: Engine = None):
    with Session(engine) as session:
        try:
            session.execute(text('DROP SCHEMA public CASCADE;'))
            session.commit()

        except Exception as e:
            log_warning(f'Suppressed exception while dropping schema: {str(e)}')

def create_schema(engine: Engine = None):
    with Session(engine) as session:
        try:
            session.execute(text('CREATE SCHEMA public;'))
            session.commit()

        except Exception as e:
            log_warning(f'Suppressed exception while creating schema: {str(e)}')


def drop_create_schema(engine: Engine) -> None:
    drop_schema(engine)
    create_schema(engine)


def sync_model_schemas(engine: Engine = None, models: list = None) -> None:
    if not models:
        log_warning('No models provided. Syncing tables for all models...')

    Base.metadata.create_all(
        bind=engine,
        tables=[model.__table__ for model in models] if models else None,
    )
