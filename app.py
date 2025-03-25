from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'my_secret_key_here'

mysql = MySQL(app)
bcrypt = Bcrypt(app)  # ✅ Correctly initializing Bcrypt

# Form class
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

# Routes
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # ✅ Correctly Hashing the Password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store in database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()  # ✅ Fixed commit method
        cursor.close()

        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

@app.route("/Dashboard")
def Dashboard():
    return render_template('Dashboard.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
