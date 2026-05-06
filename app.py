from flask import Flask, render_template, redirect, url_for, request, flash, abort
from models import db, Project, Task
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    projects = Project.query.order_by(Project.start_date.desc()).all()
    return render_template('index.html', projects=projects)


@app.route('/project/new', methods=['GET', 'POST'])
def project_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if not name:
            flash('Название проекта обязательно', 'error')
            return render_template('project_form.html', project=None)

        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
        end_date = date.fromisoformat(end_date_str) if end_date_str else None

        if end_date and end_date < start_date:
            flash('Дата окончания не может быть раньше даты начала', 'error')
            return render_template('project_form.html', project=None)

        project = Project(name=name, description=description, start_date=start_date, end_date=end_date)
        db.session.add(project)
        db.session.commit()
        flash('Проект создан!', 'success')
        return redirect(url_for('project_detail', project_id=project.id))

    return render_template('project_form.html', project=None)


@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.created_at.desc()).all()
    return render_template('project_detail.html', project=project, tasks=tasks)


@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def project_edit(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if not name:
            flash('Название проекта обязательно', 'error')
            return render_template('project_form.html', project=project)

        start_date = date.fromisoformat(start_date_str) if start_date_str else project.start_date
        end_date = date.fromisoformat(end_date_str) if end_date_str else None

        if end_date and end_date < start_date:
            flash('Дата окончания не может быть раньше даты начала', 'error')
            return render_template('project_form.html', project=project)

        project.name = name
        project.description = description
        project.start_date = start_date
        project.end_date = end_date
        db.session.commit()
        flash('Проект обновлён', 'success')
        return redirect(url_for('project_detail', project_id=project.id))

    return render_template('project_form.html', project=project)


@app.route('/project/<int:project_id>/delete', methods=['POST'])
def project_delete(project_id):
    project = Project.query.get_or_404(project_id)
    # Удаляем каскадно — всё равно данные в задачах уже "принадлежат" проекту
    for task in project.tasks:
        db.session.delete(task)
    db.session.delete(project)
    db.session.commit()
    flash(f'Проект «{project.name}» удалён вместе со всеми задачами', 'info')
    return redirect(url_for('index'))


@app.route('/project/<int:project_id>/task/new', methods=['GET', 'POST'])
def task_new(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status')
        priority = request.form.get('priority')
        assignee = request.form.get('assignee', '').strip()

        if not name:
            flash('Название задачи обязательно', 'error')
            return render_template('task_form.html', project=project, task=None)

        task = Task(
            name=name,
            description=description,
            status=status,
            priority=priority,
            assignee=assignee,
            project_id=project_id
        )
        db.session.add(task)
        db.session.commit()
        flash('Задача добавлена', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template('task_form.html', project=project, task=None)


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def task_edit(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Название задачи обязательно', 'error')
            return render_template('task_form.html', project=project, task=task)

        task.name = name
        task.description = request.form.get('description', '').strip()
        task.status = request.form.get('status')
        task.priority = request.form.get('priority')
        task.assignee = request.form.get('assignee', '').strip()
        db.session.commit()
        flash('Задача обновлена', 'success')
        return redirect(url_for('project_detail', project_id=project.id))

    return render_template('task_form.html', project=project, task=task)


@app.route('/task/<int:task_id>/delete', methods=['POST'])
def task_delete(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash(f'Задача «{task.name}» удалена', 'info')
    return redirect(url_for('project_detail', project_id=project_id))


if __name__ == '__main__':
    app.run(debug=True)
