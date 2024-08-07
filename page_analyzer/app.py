from flask import Flask, render_template, request, flash, redirect, url_for
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from datetime import date
from page_analyzer.db import DataBase
from validators.url import url as check_url
from urllib.parse import urlparse
import requests


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
db = DataBase(DATABASE_URL)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html'), 404


@app.route("/")
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.route("/urls/<id>")
def urls_id(id):
    record = db.get_record_by_url_id('urls', id)
    if record:
        checks = db.get_checks_by_url_id('url_checks', id)
        return render_template('urls_id.html', record=record, checks=checks)
    else:
        return render_template('page404.html'), 404


@app.get('/urls')
def get_urls():
    data = db.join_url_checks('urls', 'url_checks')
    return render_template('urls.html', data=data)


@app.post('/urls')
def post_urls():
    request_url = request.form['url']
    if check_url(request_url):
        data = db.read_all_data('urls')
        parsed_url = urlparse(request_url)
        current_url = f'{parsed_url.scheme}://{parsed_url.hostname}'
        urls = [f'{urlparse(record["url"]).scheme}://{urlparse(record["url"]).hostname}' for record in data]
        if current_url in urls:
            flash('Страница уже существует', 'info')
            id_generator = (
                record['id']
                for record in data
                if f'{urlparse(record["url"]).scheme}://{urlparse(record["url"]).hostname}' == current_url
            )
            id = next(id_generator, None)
            return redirect(url_for('urls_id', id=id))
        else:
            next_id = data[-1]['id'] + 1 if data else 1
            insert_data = {'id': next_id, 'url': current_url, 'created_at': str(date.today())}
            db.insert('urls', insert_data)
            data = db.read_all_data('urls')
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('urls_id', id=next_id))
    else:
        flash("Некорректный URL", 'danger')
        return render_template('index.html'), 422


@app.post('/urls/<id>/checks')
def check(id):
    data = db.read_all_data('url_checks')
    record = db.get_record_by_url_id('urls', id)
    try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'} # noqa E501
        print(f'[INFO] Waiting response from {record["url"]}')
        response = requests.get(record['url'], headers=headers)
        print(f'[INFO] Got response from {record["url"]}')
        response.raise_for_status()
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        checks = db.get_checks_by_url_id('url_checks', id)
        return render_template('urls_id.html', record=record, checks=checks)
    else:
        flash('Страница успешно проверена', 'success')
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = soup.find('h1')
        next_id = data[-1]['id'] + 1 if data else 1
        title = soup.find('title')
        content = soup.find('meta', attrs={'name': 'description'})
        insert_data = {'id': next_id,
                       'url_id': id,
                       'status_code': response.status_code,
                       'h1': h1.get_text() if h1 else '',
                       'title': title.get_text() if title else '',
                       'description': content['content'] if content else '',
                       'created_at': str(date.today())}
        db.insert('url_checks', insert_data)
    return redirect(url_for('urls_id', id=id))
