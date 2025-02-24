from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('game/home.html')

@app.route('/start')
def start():
    return render_template('game/start.html')

if __name__ == '__main__':
    app.run(debug=True)