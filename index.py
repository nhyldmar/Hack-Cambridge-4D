from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/') #root directory
def index():
    language = request.args.get('language')
    return render_template("/index.html")



if __name__ == "__main__":
    app.run(debug=True) #debug =True -> developer mode 