from .connection import get_database
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime, date
import validators
from urllib.parse import urlparse
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)


@app.route('/')
def starting_page():
    return render_template(
        'index.html'
    )


@app.get('/urls')
def get_page():
    db = get_database()
    curr = db.cursor()
    curr.execute("SELECT * FROM urls;")
    urls_ = curr.fetchall()
    curr.close()
    db.close()
    return render_template(
        'urls/index.html',
        data=urls_
    )

@app.post('/urls')
def insert_url():
    db = get_database()
    curr = db.cursor()
    url = request.form['url']
    if validators.url(url):
        parsed_url = urlparse(url)
        normalized_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        curr.execute(f'INSERT INTO urls (name, created_at)'
                    f" VALUES ('{normalized_url}', '{date.today()}');")
        db.commit()
        curr.execute("SELECT id, name, created_at FROM urls WHERE name = %s", (normalized_url,))
        result = curr.fetchall()[0]
        curr.close()
        db.close()
        return redirect(f"urls/{result[0]}")
    else:
        return redirect(
            '/')


@app.route('/urls/<int:id>')
def show_specific_url(id):
    db = get_database()
    curr = db.cursor()
    curr.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (str(id),))
    result = curr.fetchall()[0]
    if not result:
        db.close()
        return render_template('/404.html'), 404
    db.close
    return render_template('urls/url_id.html',
                           result=result)
    