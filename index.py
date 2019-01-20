from flask import Flask, render_template
from flask import request
app = Flask(__name__)

@app.route('/') #root directory
def index():
    return render_template("/index.html")

@app.route('/data')
def dataroute():
    print("Received data - (" + request.args["0i"] + ", " + request.args["0j"] + ")")
    print("got data")
    print('data:')
    data = [[request.args["0i"],request.args["0j"]],[request.args["1i"],request.args["1j"]],[request.args["2i"],request.args["2j"]]]
    print("wav1", data[0])
    print("wav2", data[1])
    print("wav3", data[2])
    return "Success."


if __name__ == "__main__":
    app.run(debug=True) #debug =True -> developer mode 