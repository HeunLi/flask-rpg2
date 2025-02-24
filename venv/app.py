from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('game/home.html')

@app.route('/start')
def start():
    return render_template('game/start.html')

@app.route('/battle')
def battle():
    print(request.args) #getting query params
    
    return render_template('battle/index.html')

if __name__ == '__main__':
    app.run(debug=True)
