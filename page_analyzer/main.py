from .connection import get_database, get_status
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   flash,
                   get_flashed_messages)
from urllib.parse import urlparse
from .db_operations import get_all_urls
from .parser import make_soup
import validators
from dotenv import load_dotenv
import os
from datetime import date


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET')


@app.route('/')
def starting_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        messages=messages
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
        curr.execute(f"SELECT id, name from urls\
                      WHERE name = '{normalized_url}';")
        check_in_db = curr.fetchone()
        if not check_in_db:
            curr.execute(f'INSERT INTO urls (name, created_at)'
                         f" VALUES ('{normalized_url}', '{date.today()}');")
            db.commit()
            curr.execute(
                "SELECT id, name, created_at\
                    FROM urls WHERE name = %s", (normalized_url,))
            result = curr.fetchone()
            curr.close()
            db.close()
            flash('Страница успешно добавлена', 'success')
            return redirect(f"urls/{result[0]}")
        else:
            flash('Страница уже существует', 'success')
            return redirect(f'urls/{check_in_db[0]}')
    else:
        flash('Некорректный URL', 'error')
        return redirect(
            '/')


@app.route('/urls/<id>')
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
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls/url_id.html',
                           result=result,
                           checks=checks,
                           messages=messages)


@app.post('/urls/<id>/checks')
def make_check(id):
    db = get_database()
    curr = db.cursor()
    curr.execute(
        "SELECT name FROM urls WHERE id = %s LIMIT 1", (str(id)))
    url = curr.fetchone()[0]
    soup = make_soup(url)
    curr.execute(
        f"INSERT INTO url_checks ("
        f"url_id, created_at, status_code, h1, title, description)"
        f" VALUES ({id}, '{date.today()}', {get_status(url)},\
              '{soup['h1']}', '{soup['title']}', '{soup['description']}')"
    )
    db.commit()
    db.close()
    return redirect(f'/urls/{int(id)}')
