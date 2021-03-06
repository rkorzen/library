import os
from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from forms import BookForm
from models import books


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "nininini"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/books/", methods=["GET", "POST"])
def books_list():
    form = BookForm()
    error = ""
    if request.method == "POST":
        if form.validate_on_submit():
            books.create(form.data)
            books.save_all()
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("File is uploaded")
            return redirect(url_for('uploaded_file', filename=filename))
        if form.validate_on_submit():
            books.create(form.data)
            books.save_all()
        return redirect(url_for("books_list"))

    return render_template("books.html", form=form, books=books.all(), error=error)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/books/<int:book_id>/", methods=["GET", "POST"])
def book_details(book_id):
    book = books.get(book_id - 1)
    form = BookForm(data=book)

    if request.method == "POST":
        if form.validate_on_submit():
            books.update(book_id - 1, form.data)
        return redirect(url_for("books_list"))
    return render_template("book.html", form=form, book_id=book_id)


if __name__ == "__main__":
    app.run(debug=True)
