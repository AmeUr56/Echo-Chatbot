from app import create_app,socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host='localhost', port=5000,debug=1,allow_unsafe_werkzeug=True)
    #app.run(host='localhost', port=5000,debug=1)