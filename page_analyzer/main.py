from .connection import get_database, get_status
from flask import Flask, render_template, request, redirect
from datetime import date
from urllib.parse import urlparse
from .db_operations import get_all_urls
import validators

app = Flask(__name__)


@app.route('/')
def starting_page():
    return render_template(
        'index.html'
    )


@app.get('/urls')
def get_page():
    db = get_database()
    result = get_all_urls(db)
    return render_template(
        'urls/index.html',
        data=result[0],
        checks=result[1],
        codes=result[2]
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
        curr.execute(
            "SELECT id, name, created_at\
                  FROM urls WHERE name = %s", (normalized_url,))
        result = curr.fetchone()
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
    curr.execute(
        "SELECT id, name, created_at FROM urls WHERE id = %s", (str(id),))
    result = curr.fetchone()
    if not result:
        db.close()
        return redirect('/404.html'), 404
    curr.execute(f"SELECT * FROM url_checks"
                 f" WHERE url_id = '{id}' ORDER BY id DESC;")
    checks = curr.fetchall()
    db.close()
    return render_template('urls/url_id.html',
                           result=result,
                           checks=checks)


@app.post('/urls/<id>/checks')
def make_check(id):
    db = get_database()
    curr = db.cursor()
    curr.execute(
        "SELECT name FROM urls WHERE id = %s LIMIT 1", (str(id)))
    url = curr.fetchone()[0]
    curr.execute(
        f"INSERT INTO url_checks ("
        f"url_id, created_at, status_code)"
        f" VALUES ({id}, '{date.today()}', {get_status(url)})"
    )
    db.commit()
    db.close()
    return redirect(f'/urls/{int(id)}')
