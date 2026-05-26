from flask import Flask, render_template
from models import db

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

# Initialize DB

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)