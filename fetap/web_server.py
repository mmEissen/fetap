import os
from flask import Flask, current_app, render_template

from fetap.storage import PhoneBook


def create_app() -> Flask:
    app = Flask(__name__)
    app.phone_book = PhoneBook(file_path=os.environ["PHONE_BOOK"])
    return app

app = create_app()

@app.route("/")
def settings_page():
    return render_template("settings.html")

@app.route("/numbers")
def settings_page():
    return (
        "<table>"
            "<tr>"
                "<th>number</th>"
                "<th>address</th>"
            "</tr>" 
            + "\n".join(
                f"<tr><td>{number}</td><td>{address}</td></tr>"
                for number, address in current_app.phone_book.list_all()
            ) + "</table>"
        + "<table>"
    )

