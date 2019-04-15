from app import create_app
from flask_script import Shell, Manager

socketio, app = create_app()
manager = Manager(app)

def make_shell_context():
    return {'app': app}

manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == "__main__":
    socketio.run(app)