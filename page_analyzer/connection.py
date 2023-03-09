import psycopg2
import requests
from dotenv import load_dotenv
import os
from requests.exceptions import HTTPError

load_dotenv()


def get_database():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def get_status(url):
    try:
        response = requests.get(url)
        return response.status_code
    except HTTPError:
        return 'bad_status'
    except Exception:
        return 'bad_status'
