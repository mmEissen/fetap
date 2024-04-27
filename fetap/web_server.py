import os
from flask import Flask, current_app, render_template

from fetap import storage, logging


def create_app() -> Flask:
    logging.configure()

    app = Flask(__name__)
    app.phone_book = storage.PhoneBook(file_path=os.environ["PHONE_BOOK"])
    return app

app = create_app()

@app.route("/")
def settings_page():
    return render_template("settings.html")

@app.route("/numbers")
def list_numbers():
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

