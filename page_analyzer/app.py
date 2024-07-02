from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import os
from datetime import date
from page_analyzer.dbfunc import insert_into_db, read_db, join_dbs
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

    data = read_db(DATABASE_URL, 'urls')
    record = [line for line in data if line['id'] == int(id)]
    # ЕСЛИ ЗАПИСЬ СУЩЕСТВУЕТ ТО
    # ПЕРЕДАЁМ ДАННЫЕ И ВОЗВРАЩАЕМ ШАБЛОН
    if record:

        # ПРОВЕРЯЕМ ЕСТЬ ЛИ ЗАПИСИ О ПРОВЕРКАХ
        data = read_db(DATABASE_URL, 'url_checks')
        checks = [{key: value for key, value in check.items()} for check in data if check['url_id'] == record[0]['id']]

        return render_template('urls_id.html', record=record[0], checks=checks)

    # В ПРОТИВНОМ СЛУЧАЕ ВОЗВАРАЩАЕМ ОШИБКУ 404 И PAGE_NOT_FOUND
    else:
        return render_template('page404.html'), 404


@app.route("/urls", methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        request_url = request.form['url']
        # ВЫПОЛНЯЕТСЯ ПРОВЕРКА НА ВАЛИДНОСТЬ URL
        if check_url(request_url):
            data = read_db(DATABASE_URL, 'urls')
            parsed_url = urlparse(request_url)
            current_url = f'{parsed_url.scheme}://{parsed_url.hostname}'
            urls = [f'{urlparse(record["url"]).scheme}://{urlparse(record["url"]).hostname}' for record in data]
            # ВЫПОЛНЯЕТСЯ ПРОВЕРКА НА НАЛИЧИЕ ДАННЫХ В БД
            if current_url in urls:
                flash('Страница уже существует')
                id = [record['id'] for record in data if f'{urlparse(record["url"]).scheme}://{urlparse(record["url"]).hostname}' == current_url] # noqa E501
                return redirect(url_for('urls_id', id=id[0]))
            else:
                # ДОБАВЛЕНИЕ СТРАНИЦЫ В БД, ПЕРЕНАПРАВЛЕНИЕ НА ПУТЬ URLS/<ID>
                created_at = str(date.today())
                next_id = data[-1]['id'] + 1 if data else 1
                insert_data = {'id': next_id, 'url': current_url, 'created_at': created_at}
                insert_into_db(DATABASE_URL, 'urls', insert_data)
                data = read_db(DATABASE_URL, 'urls')
                flash('Страница успешно добавлена')
                return redirect(url_for('urls_id', id=next_id))
        else:
            flash("Некорректный URL")
            return redirect(url_for('index'))
    elif request.method == 'GET':
        data = join_dbs(DATABASE_URL, 'urls', 'url_checks')
        return render_template('urls.html', title='Анализатор страниц', data=data)


@app.post('/urls/<id>/checks')
def check(id):
    # ЧИТАЕМ ПОСЛЕДНИЙ ID И ПРИСВАИВАЕМ СЛЕДУЮЩЕМУ НА ЕДИНИЦУ БОЛЬШЕ
    data = read_db(DATABASE_URL, 'url_checks')
    next_id = data[-1]['id'] + 1 if data else 1
    created_at = str(date.today())
    insert_data = {'id': next_id,
                   'url_id': id,
                   'status_code': int(),
                   'h1': '',
                   'description': '',
                   'created_at': created_at}
    insert_into_db(DATABASE_URL, 'url_checks', insert_data)
    return redirect(url_for('urls_id', id=id))
