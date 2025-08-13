from flask import Flask

app = Flask(__name__)
print("RUNNING FILE:", __file__)

@app.route("/", methods=["GET"])
def index():
    return "SANITY OK - Pathwise server"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
