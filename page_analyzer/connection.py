import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()


def get_database():
    return psycopg2.connect(os.getenv('DATABASE_URL'))
