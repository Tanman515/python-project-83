from flask import Flask
from python-dotenv import load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'
