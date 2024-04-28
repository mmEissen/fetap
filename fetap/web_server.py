import os
from flask import Flask, current_app, render_template, request, redirect, url_for

from fetap import storage, logging


def create_app() -> Flask:
    logging.configure()

    app = Flask(__name__)
    app.phone_book = storage.PhoneBook(file_path=os.environ["PHONE_BOOK"])
    return app

app = create_app()

@app.route("/")
def home_page():
    phone_book: storage.PhoneBook = current_app.phone_book
    return render_template("list_numbers.html", entries=phone_book.list_all())

@app.route("/add-number", methods=["GET", "POST"])
def add_number():
    if request.method == "POST":
        return add_number_post()
    return render_template("add_number.html")

def add_number_post():
    address = request.form.get("address")
    number = request.form.get("number")

    if address is None or number is None:
        return 400, "address and number can't be None"
    address = str(address)
    number = str(number)

    phone_book: storage.PhoneBook = current_app.phone_book
    try:
        phone_book.insert(number, address)
    except storage.NumberExists:
        return 400, "Number exists"
    except storage.AddressExists:
        return 400, "address exists"

    return redirect(url_for("home_page"))