from flask import Flask, render_template, session,flash,request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email,ValidationError
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from wtforms import SelectField

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'my_secret_key_here'

def get_enum_values():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SHOW COLUMNS FROM user LIKE 'role'")
        result = cursor.fetchone()
        cursor.close()

        if result:
            # Extract ENUM values from the result
            enum_str = result[1]  # This contains the ENUM values in a string
            enum_values = enum_str.replace("enum(", "").replace(")", "").replace("'", "").split(",")
            return enum_values
        else:
            return []  # Return an empty list if no 'role' column or ENUM found
    except Exception as e:
        print("Error fetching enum values:", e)
        return []  # Return an empty list if an error occurs



mysql = MySQL(app)
bcrypt = Bcrypt(app)  # ✅ Correctly initializing Bcrypt

# Form class
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    role = SelectField("Role", choices=[], validators=[DataRequired()])
    submit = SubmitField("Register")
    
    def validate_email(self,field):
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM user where email=%s",(field.data,))
        user=cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError("Email is already taken.")
    
    
class loginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class CommitteeForm(FlaskForm):
    name = StringField("Committee Name", validators=[DataRequired()])
    submit = SubmitField("Create Committee")




class AddMemberForm(FlaskForm):
    user_id = SelectField("Select User", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Add Member")

# Routes

@app.route("/")
def home():
    return redirect('login')

@app.route("/login",methods=["GET","POST"])
def login():
    form =loginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email=%s",(email,))
        user=cursor.fetchone()
        cursor.close()
        if user and bcrypt.check_password_hash(user[3],password):
            session['user_id']=user[0]
            return redirect(url_for('Dashboard'))
        else :
            flash("Login failed")
            return redirect('login')
    return render_template("login.html",form=form,active_page='login')
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # Initialize roles to an empty list by default
    roles = get_enum_values()  # Get enum values

    if not roles:
        roles = []  # If roles is empty, ensure it's set to an empty list

    form = RegisterForm()
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash the password before storing in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                       (name, email, hashed_password, form.role.data))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))
    
    return render_template("signup.html", form=form, active_page='signup', roles=roles)


@app.route("/Dashboard")
def Dashboard():
    if 'user_id' in session:
        user_id =session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user where id =%s",(user_id,))
        user=cursor.fetchone()
        cursor.close()
    else :
        user=None
    if user:
        return render_template('Dashboard.html',user=user,active_page='Dashboard')
    else :
        
        return render_template('Dashboard.html',user=user,active_page='Dashboard')
@app.route("/logout")
def logout():
    session.pop("user_id",None)
    flash("You have been log out successfully.")
    return redirect(url_for("login"))

@app.route("/committees/create", methods=['GET', 'POST'])
def create_committee():
    form = CommitteeForm()
    if form.validate_on_submit():
        name = form.name.data
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO committees (name) VALUES (%s)", (name,))
        mysql.connection.commit()
        cursor.close()
        flash("Committee created successfully.")
        return redirect(url_for("list_committees"))
    return render_template("create_committee.html", form=form)

@app.route("/committees")
def list_committees():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM committees")
    committees = cursor.fetchall()
    cursor.close()
    return render_template("committees.html", committees=committees)

@app.route("/committees/<int:committee_id>/add_member", methods=['GET', 'POST'])
def add_member(committee_id):
    form = AddMemberForm()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM user")
    users = cursor.fetchall()
    form.user_id.choices = [(u[0], u[1]) for u in users]

    if form.validate_on_submit():
        user_id = form.user_id.data
        cursor.execute("INSERT INTO committee_members (user_id, committee_id) VALUES (%s, %s)", 
                       (user_id, committee_id))
        mysql.connection.commit()
        cursor.close()
        flash("Member added successfully.")
        return redirect(url_for("view_committee", committee_id=committee_id))

    return render_template("add_member.html", form=form)


@app.route("/committees/<int:committee_id>")
def view_committee(committee_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name FROM committees WHERE id=%s", (committee_id,))
    committee = cursor.fetchone()

    cursor.execute("""
        SELECT u.id, u.name, u.email 
        FROM user u
        JOIN committee_members cm ON u.id = cm.user_id
        WHERE cm.committee_id = %s
    """, (committee_id,))
    members = cursor.fetchall()
    cursor.close()

    return render_template("view_committee.html", committee=committee, members=members)

        
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
