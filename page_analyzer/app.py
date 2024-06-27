from flask import Flask, render_template, request
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.route("/urls", methods=["GET", "POST"])
def urls():
    if request.method == "POST":
        request_url = request.form['url']
    return render_template('urls.html', title='Анализатор страниц')
