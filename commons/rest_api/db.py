from sqlalchemy import text
from sqlalchemy.engine import Engine

from commons.logging import log_error, log_info, log_success


def create_connection_string(
    db_user: str,
    password: str,
    db_host: str,
    db_port: int,
    db_name: str,
    driver: str = 'postgresql',
) -> str:
    return f'{driver}://{db_user}:{password}@{db_host}:{db_port}/{db_name}'


def drop_sqlalchemy_schema(engine: Engine) -> None:
    with engine.connect() as conn:
        try:
            log_info('Dropping schema...')
            conn.execute(text('drop schema public cascade;'))
            conn.commit()
            log_success('Schema dropped.')

        except Exception as e:
            log_error(f'Error dropping the schema: {e}')

        finally:
            conn.close()


def create_sqlalchemy_schema(engine: Engine) -> None:
    with engine.connect() as conn:
        try:
            log_info('Creating schema...')
            conn.execute(text('create schema public;'))
            conn.commit()
            log_success('Schema created.')

        except Exception as e:
            log_error(f'Error creating the schema: {e}')

        finally:
            conn.close()
