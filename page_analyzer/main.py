from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   flash,
                   get_flashed_messages,
                   url_for)
from .db import (get_all_urls,
                 make_insert,
                 get_database,
                 db_select)
from urllib.parse import urlparse
from .parser import parse_html
from dotenv import load_dotenv
from datetime import date
import validators
import os
import requests


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def get_status(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.HTTPError:
        return 'bad_status'
    except Exception:
        return 'bad_status'


@app.route('/')
def index():
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
        data=result['urls'],
        checks=result['checks'],
        codes=result['status_codes']
    )


@app.post('/urls')
def post_url():
    url = request.form['url']
    if validators.url(url):
        parsed_url = urlparse(url)
        normalized_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        check_in_db = db_select("id", "urls", "name", normalized_url)
        if not check_in_db:
            make_insert('urls', '(name, created_at)',
                        (normalized_url, str(date.today())))
            result = db_select("id", "urls", "name", normalized_url)
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('get_url', id=result[0]))
        else:
            flash('Страница уже существует', 'info')
            return redirect(url_for('get_url', id=check_in_db[0]))
    else:
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url_name=url), 422


@app.route('/urls/<id>')
def get_url(id):
    site = db_select("id, name, created_at", "urls", "id", id)
    if not site:
        return redirect('/404.html'), 404
    checks = db_select('*', 'url_checks', 'url_id', id, order='id DESC')
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls/url_id.html',
                           result=site,
                           checks=checks,
                           messages=messages)


@app.post('/urls/<int:id>/checks')
def post_check(id):
    url = db_select('name', 'urls', 'id', id, limit=1)[0]
    if get_status(url) == 200:
        html = parse_html(url)
        make_insert('url_checks', '(url_id, created_at,\
                     status_code, h1, title, description)',
                    (str(id), str(date.today()), str(get_status(url)),
                        html['h1'], html['title'],
                        html['description']))
        flash('Страница успешно проверена', 'success')

    else:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('get_url', id=id))
