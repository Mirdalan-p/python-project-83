import psycopg2
import requests
from dotenv import load_dotenv
import os


load_dotenv()


def get_database():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def get_status(url):
    r = requests.get(url)
    return r.status_code