from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Renders the index.html file found in the 'templates' folder
    return render_template("index.html")

if __name__ == "__main__":
    # Runs the application on a local server
    app.run(debug=True)