from flask import Flask
from modules.routes import setup_routes

app = Flask(__name__)
app.secret_key = 'mark321654'
setup_routes(app)

if __name__ == '__main__':
    app.run(debug=False)
