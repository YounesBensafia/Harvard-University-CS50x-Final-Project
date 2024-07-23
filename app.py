from flask import flash, Flask, render_template, request, session, redirect
from flask_session import Session
import sqlite3
from flask_bcrypt import Bcrypt 
from functools import wraps
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database

db = sqlite3.connect('todo.db')
db.row_factory = sqlite3.Row



bcrypt = Bcrypt(app) 


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    return render_template("index.html")



@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    db = get_db_connection()
    if request.method == "POST":
        email = request.form.get("email")
        rows = db.execute("SELECT * FROM users WHERE email = ?", (email,))      
        rows = list(rows)
        if len(rows) == 0: return render_template("login.html", message="This email doesn't exist")
        elif not bcrypt.check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("login.html", message="Invalid password")
        
        session["user_id"] = rows[0][0]
        return redirect("main")
    return render_template('login.html')

def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/main', methods=["GET", "POST"])
@login_required
def main():
    user_id = session["user_id"]
    conn = get_db_connection()
    if request.method == "POST":
        task = request.form.get("task")
        default_state = -1 # Replace with the default state value
        try:
            conn.execute("INSERT INTO tasks(user_id, title, state) VALUES(?, ?, ?)", (user_id, task, default_state))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
        return redirect('/main')
    else:
        try:
            rows = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            rows = []
        finally:
            conn.close()
        return render_template("main.html", tasks=rows)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    db = get_db_connection()
    if request.method == "POST":
        if request.form.get("password") != request.form.get("confi_pass"):
            return render_template("signup.html", error="Password does not match")
        hashed_password = bcrypt.generate_password_hash \
                (request.form.get("password")).decode('utf-8')
        # if(bcrypt.check_password_hash(hashed_password, "1")): print("ok")
        try:
            db.execute("INSERT INTO users(email, password_hash) VALUES(?, ?)", (request.form.get("email"), hashed_password))
            db.commit()
            flash("added")
            return redirect('/')
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="User already exist")
        except:
            return render_template("login.html", message="Something went wrong")
        
    return render_template("signup.html")

i = 1

@app.route('/do', methods=["GET", "POST"])
@login_required
def do():
    user_id = session["user_id"]
    global i
    db = get_db_connection()
    if request.method == "POST":
        value = request.form.get("id_button")
        if request.form.get("buttonDo") == "button1":
            row = db.execute("SELECT state FROM tasks where id = ? and user_id = ? LIMIT 1", (value, user_id)).fetchall()
            row=list(row)
            
            
            
            print(row[0][0])
            if row[0][0] == -1:
                try:
                    db.execute("UPDATE tasks SET state = ? where id = ? and user_id = ?",(1 , value, user_id))
                    db.commit()
                except:
                    return render_template("login.html", message="Database error")
            elif row[0][0] == 1:
                try:
                    db.execute("UPDATE tasks SET state = ? where id = ? and user_id = ?",(-1 , value, user_id))
                    db.commit()
                except:
                    return render_template("login.html", message="Database error")
        elif request.form.get("buttonDo") == "button2":
            db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?",(value, user_id))
            db.commit()
    return redirect("/main")

@app.route('/logout')
@login_required
def logout():
        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")
        

if __name__ == "__main__":
    app.run(debug=True)
