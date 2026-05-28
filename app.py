from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.secret_key = "supersecretkey"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"

db = SQLAlchemy(app)

class ContactMessage(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100))

    message = db.Column(db.Text)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/portfolio")
def portfolio():

    projects = [

        {
            "title": "Business Website",
            "description": "Modern responsive Flask website.",
            "image": "project1.jpg"
        },

        {
            "title": "Python Automation Tool",
            "description": "Automated Excel and reporting system.",
            "image": "project2.jpg"
        },

        {
            "title": "API Dashboard",
            "description": "Dashboard with API integrations.",
            "image": "project3.jpg"
        }

    ]

    return render_template(
        "portfolio.html",
        projects=projects
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        new_message = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        db.session.add(new_message)

        db.session.commit()

        return render_template("contact.html", success=True)

    return render_template("contact.html")


@app.route("/admin")
def admin():

    if "user" not in session:

        return redirect(url_for("login"))

    messages = ContactMessage.query.all()

    return render_template(
        "admin.html",
        messages=messages
    )



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if username == "admin" and password == "1234":

            session["user"] = username

            return redirect(url_for("admin"))

        else:

            return render_template(
                "login.html",
                error="Invalid credentials"
            )

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



