#model/pgsql_test.py


import psycopg
import psycopg_pool
from config import config

pool_default = psycopg_pool.ConnectionPool(
    config.PGSQL_TEST_DATABASE_STRING, 
    min_size=config.PGSQL_TEST_POOL_MIN_SIZE,
    max_size=config.PGSQL_TEST_POOL_MAX_SIZE,
    max_idle=config.PGSQL_TEST_POOL_MAX_IDLE
    
    
)
def list_admin():
    with pool_default.connection() as conn:
        cur = conn.cursor(row_factory=psycopg.rows.dict_row)

        try:
            # refcursor를 명시적으로 넘기기 위해 CAST 사용
            cur.execute("CALL sp_l_admin(CAST(%s AS refcursor))", ('admin_cursor',)) #sp_l_admin procedure use test
            cur.execute("FETCH ALL FROM admin_cursor")
            results = cur.fetchall()

            conn.commit()
        except psycopg.OperationalError as err:
            print(f'Error querying: {err}')
        except psycopg.ProgrammingError as err:
            print('Database error via psycopg.     %s', err)
            results = False
        except psycopg.IntegrityError as err:
            print('postgresSQL integrity error via psycopg.    %s', err)
            results = False


    return results

"""
def list_admin():
    with pool_default.connection() as conn:
        cur = conn.cursor(row_factory=psycopg.rows.dict_row)

        try:
            results = cur.execute("SELECT * FROM users").fetchall() #raw query test
        except psycopg.OperationalError as err:
            print(f'Error querying: {err}')
        except psycopg.ProgrammingError as err:
            print('Database error via psycopg.     %s', err)
            results = False
        except psycopg.IntegrityError as err:
            print('postgresSQL integrity error via psycopg.    %s', err)
            results = False


    return results
"""