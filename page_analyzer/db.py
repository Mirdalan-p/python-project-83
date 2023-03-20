import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()


def get_database():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def get_all_urls(db):
    curr = db.cursor()
    curr.execute("SELECT * FROM urls;")
    urls = curr.fetchall()
    checks = {}
    status_codes = {}
    for url in urls:
        curr.execute(f"SELECT created_at, status_code, h1,\
                      title, description FROM url_checks"
                     f" WHERE url_id = '{url[0]}' ORDER BY"
                     f" created_at DESC LIMIT 1;")
        actual_info = curr.fetchone()
        if actual_info:
            checks[url[0]] = actual_info[0]
            status_codes[url[0]] = actual_info[1]
        else:
            checks[url[0]] = ''
            status_codes[url[0]] = ''
    curr.close()
    return {'urls': urls, 'checks': checks, 'status_codes': status_codes}


def make_insert(table, fields, values):
    db = get_database()
    curr = db.cursor()
    curr.execute(f'INSERT INTO {table} {str(fields)} VALUES {str(values)};')
    db.commit()
    db.close


def db_select(fields, table, field, value, order=None, limit=0):
    db = get_database()
    curr = db.cursor()
    if limit:
        curr.execute(
            f"SELECT {fields} FROM {table} WHERE {field}"
            f" = '{str(value)}' LIMIT {str(limit)}")
        result = curr.fetchone()
        db.close
        return result
    elif order:
        curr.execute(
            f"SELECT {fields} FROM {table} WHERE {field}"
            f" = '{str(value)}' ORDER BY {order}")
        result = curr.fetchall()
        db.close
        return result
    else:
        curr.execute(
            f"SELECT {fields} FROM {table} WHERE {field} = '{str(value)}'")
        result = curr.fetchone()
        db.close
        return result
