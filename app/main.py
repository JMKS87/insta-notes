from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/<name>", methods=["GET"])
def get_note(name):
    context = {"name": name}
    return render_template("notes.html", context=context)


@app.route("/<name>", methods=["POST"])
def post_note(name):
    context = {"name": 'not yet'}
    return render_template("notes.html", context=context)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
