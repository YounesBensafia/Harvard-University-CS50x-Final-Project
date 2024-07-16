from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        younes = request.form.get("email")
        return render_template("test.html", younes=younes)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if request.form.get("password") != request.form.get("confi_pass"):
            # return "ffjke", 400
            return render_template("signup.html", error="Password does not match")
        
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
