from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import os
from datetime import date
from page_analyzer.dbfunc import insert_into_db, read_db
from validators.url import url as check_url
from urllib.parse import urlparse


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html'), 404


@app.route("/")
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.route("/urls/<id>")
def urls_id(id):

    # ПРОВЕРЯЕМ ЕСТЬ ЛИ УКАЗАННЫЙ ID В БД
    # ЕСЛИ ЕСТЬ ОТПРАВЛЯЕМ HTML
    # В ПРОТИВНОМ СЛУЧАЕ ОШИБКУ 404

    data = read_db(DATABASE_URL)
    record = [line for line in data if line['id'] == int(id)]
    # ЕСЛИ ЗАПИСЬ СУЩЕСТВУЕТ ТО
    # ПЕРЕДАЁМ ДАННЫЕ И ВОЗВРАЩАЕМ ШАБЛОН
    if record:
        return render_template('urls_id.html', id=id, url=record[0]['url'], created_at=record[0]['created_at'])

    # В ПРОТИВНОМ СЛУЧАЕ ВОЗВАРАЩАЕМ ОШИБКУ 404 И PAGE_NOT_FOUND
    else:
        return render_template('page404.html'), 404


@app.route("/urls", methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        request_url = request.form['url']
        # ВЫПОЛНЯЕТСЯ ПРОВЕРКА НА ВАЛИДНОСТЬ URL
        if check_url(request_url):
            data = read_db(DATABASE_URL)
            request_hostname = urlparse(request_url).hostname
            urls = [urlparse(record['url']).hostname for record in data]
            # ВЫПОЛНЯЕТСЯ ПРОВЕРКА НА НАЛИЧИЕ ДАННЫХ В БД
            if request_hostname in urls:
                flash('Страница уже существует')
                id = [record['id'] for record in data if urlparse(record['url']).hostname == request_hostname]
                return redirect(url_for('urls_id', id=id[0]))
            else:
                # ДОБАВЛЕНИЕ СТРАНИЦЫ В БД, ПЕРЕНАПРАВЛЕНИЕ НА ПУТЬ URLS/<ID>
                created_at = str(date.today())
                next_id = data[-1]['id'] + 1 if data else 1
                insert_into_db(DATABASE_URL, next_id, request_url, created_at)
                data = read_db(DATABASE_URL)
                flash('Страница успешно добавлена')
                return redirect(url_for('urls_id', id=next_id))
        else:
            flash("Некорректный URL")
            return redirect(url_for('index'))
    elif request.method == 'GET':
        data = read_db(DATABASE_URL, order='DESC')
        return render_template('urls.html', title='Анализатор страниц', data=data)
