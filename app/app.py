from flask import Flask
from flask import render_template,request, jsonify
from .ghabz.routes import ghabz_bp

app = Flask(__name__)
app.register_blueprint(ghabz_bp)

@app.route('/')
def home():

    return 'Hello, World!'




# if ___main___name__ == '':
#     app.run(debug=True)

# app.run(debug=True)
