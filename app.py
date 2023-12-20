from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ba8f2cc5d143cc4647730ba51111a169252b90c94f69d29fc25d60c3ec3fc691'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/passmanager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    password_entries = db.relationship('PasswordEntry', backref='user', lazy=True)

class PasswordEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already in use. Please choose a different email.', 'error')
        else:
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

# ... (Continuation from the previous code)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        user = User.query.get(user_id)

        if user:
            password_entries = user.password_entries
            return render_template('dashboard.html', password_entries=password_entries)

    flash('You need to log in first.', 'warning')
    return redirect(url_for('login'))

@app.route('/add_password', methods=['POST'])
def add_password():
    if request.method == 'POST':
        user_id = session['user_id']
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        website = request.form['website']
        password = request.form['password']

        user = User.query.get(user_id)

        if user:
            new_password_entry = PasswordEntry(user_id=user_id, name=name, username=username, email=email, website=website, password=password)
            db.session.add(new_password_entry)
            db.session.commit()

            flash('Password entry added successfully.', 'success')

    return redirect(url_for('dashboard'))

@app.route('/edit_password/<int:entry_id>', methods=['GET'])
def edit_password(entry_id):
    # Retrieve the password entry with the given ID from the database
    password_entry = PasswordEntry.query.get(entry_id)

    # Perform any necessary logic for editing (e.g., pre-fill a form)
    return render_template('edit_password.html', password_entry=password_entry)

@app.route('/delete_password/<int:entry_id>', methods=['POST'])
def delete_password(entry_id):
    # Delete the password entry with the given ID from the database
    password_entry = PasswordEntry.query.get(entry_id)

    if password_entry:
        db.session.delete(password_entry)
        db.session.commit()

        flash('Password entry deleted successfully.', 'success')

    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
