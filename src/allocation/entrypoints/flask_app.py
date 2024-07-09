from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "OK", 200


@app.route("/allocate")
def allocate_endpoint():
    return "OK", 200


# @app.route("/allocate", methods=["POST"])
# def allocate_endpoint():
#     return "OK", 201
