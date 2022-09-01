from sqlalchemy import text
from sqlalchemy.engine import Engine

from commons.logging import log_error, log_info, log_success


def create_connection_string(
    user: str,
    password: str,
    hostname: str,
    port: int,
    database: str,
    driver: str = 'postgresql',
) -> str:
    return f'{driver}://{user}:{password}@{hostname}:{port}/{database}'


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
