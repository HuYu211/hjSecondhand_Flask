from flask import Flask
from controllers.api.hjSeconhand import route_api
from flask_socketio import SocketIO, emit
app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
app.register_blueprint(route_api,url_prefix='/api')

@app.route('/')
def hello_world():
    return 'Hello World!'





if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app, debug=True)
    # socketio.run(app)
