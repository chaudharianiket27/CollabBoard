from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hackathon-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Task model
class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)

# Create database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# SocketIO events
@socketio.on('add_task')
def handle_add_task(data):
    task = Task(id=str(uuid.uuid4()), title=data['title'], status=data['status'])
    db.session.add(task)
    db.session.commit()
    emit('task_added', {'id': task.id, 'title': task.title, 'status': task.status}, broadcast=True)

@socketio.on('update_task')
def handle_update_task(data):
    task = Task.query.get(data['id'])
    if task:
        task.status = data['status']
        db.session.commit()
        emit('task_updated', {'id': task.id, 'status': task.status}, broadcast=True)

@socketio.on('delete_task')
def handle_delete_task(data):
    task = Task.query.get(data['id'])
    if task:
        db.session.delete(task)
        db.session.commit()
        emit('task_deleted', {'id': data['id']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)