from flask import Flask
from models import db

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

# Initialize database

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return '<h1>Database Connected</h1>'

if __name__ == '__main__':
    app.run(debug=True)