from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

db = SQLAlchemy()


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)

    tasks = db.relationship('Task', backref='project', lazy=True)

    def progress(self):
        total = len(self.tasks)
        if total == 0:
            return 0
        done = sum(1 for t in self.tasks if t.status == 'Завершена')
        return round(done / total * 100)


class Task(db.Model):
    __tablename__ = 'tasks'

    STATUS_CHOICES = ['Новая', 'В работе', 'На проверке', 'Завершена']
    PRIORITY_CHOICES = ['Низкий', 'Средний', 'Высокий']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(50), nullable=False, default='Новая')
    priority = db.Column(db.String(50), nullable=False, default='Средний')
    assignee = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
