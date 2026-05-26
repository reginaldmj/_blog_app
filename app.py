from flask import Flask, render_template, redirect, url_for
from werkzeug.security import generate_password_hash
from models import db, User
from forms import RegisterForm

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)