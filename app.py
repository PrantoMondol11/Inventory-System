from flask import *
from flask_wtf import Form
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import *
import bcrypt
from flask_mysqldb import MySQL
app = Flask(__name__)


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mydatabase'
app.secret_key='my_secret_key_here'
mysql = MySQL(app)
class RegisterForm(Form):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired(),Email()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Register")
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/signup")
def signup():
    form=RegisterForm()
    if form.validate_on_submit():
        name=form.name.data
        email=form.email.data
        password=form.password.data
        
        hashed_password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        #database store
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user(name,email,password) VALUES(%s,%s,%s)",(name,email,hashed_password))
        mysql.connect.commit()
        cursor.close()
        
        return redirect(url_for('login'))
@app.route("/Dashboard")
def Dashboard():
    return render_template('Dashboard.html')

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)