from flask import Flask, render_template, send_file
from flask_bootstrap import Bootstrap
import json
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
Bootstrap(app)


def get_content():
    with open("static/files/source.json") as content:
        content = json.loads(content.read())

    return content


@app.route('/')
def home():
    return render_template("index.html", content=get_content())


@app.route('/iwantresume')
def give_resume():
    file = f'static/files/resume_mWelpa.pdf'
    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5001)




