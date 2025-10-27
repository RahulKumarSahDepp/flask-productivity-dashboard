from flask import Flask, render_template, request, redirect, url_for, jsonify, flash,session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'RahulSahProductivityDashboard2025SuperDataAnalysisProject03'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "DepthFirst",
        database = "productivity"
    )
    return conn


# -----------------------------
# User Model
# -----------------------------
class User(UserMixin):
    def __init__(self, id, username, email, password_hash, profile_image='profile.png'):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.profile_image = profile_image
# -----------------------------
# User Loader for Flask-Login
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(
            user['id'],
            user['username'],
            user['email'],
            user['password_hash'],
            user.get('profile_image', 'profile.png')
        )
    return None

# -----------user register route -------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, hashed_password))
        conn.commit()
        conn.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


# ----------Login route------------
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email, ))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['email'], user['password_hash'])
            login_user(user_obj)
            flash("Log in successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials.", "danger")
    return render_template('login.html')
                                             
# ----------Logout route------------
@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("You have been loged Out!", "info")
    return redirect(url_for('login'))


# --------Users profile setting-------
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form.get('password')

        file = request.files.get('profile_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{current_user.id}." + file.filename.rsplit('.', 1)[1].lower())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = current_user.profile_image  # Keep existing image

        # ✅ Update password only if provided
        if password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, password_hash=%s, profile_image=%s WHERE id=%s",
                (username, email, hashed_password, filename, current_user.id)
            )
        else:
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, profile_png=%s WHERE id=%s",
                (username, email, filename, current_user.id)
            )

        conn.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    # Load user data for display
    cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

# ---------- Home / Index ----------
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')

    # Base query — only tasks belonging to the logged-in user
    query = """
        SELECT id, title, category, duration, date, status, deadline, progress,
               CASE WHEN deadline IS NOT NULL AND deadline < CURDATE() AND status <> 'Completed' THEN 1 ELSE 0 END AS overdue
        FROM tasks
        WHERE user_id = %s
    """
    params = [current_user.id]

    if search_query:
        query += " AND (title LIKE %s OR category LIKE %s OR status LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)

    if category_filter:
        query += " AND category = %s"
        params.append(category_filter)

    query += " ORDER BY date DESC"
    cursor.execute(query, tuple(params))
    tasks = cursor.fetchall()

    # Totals and stats (filtered per user — unchanged logic)
    cursor.execute(
        "SELECT SUM(duration) AS total_duration, AVG(duration) AS avg_duration FROM tasks WHERE user_id = %s",
        (current_user.id,)
    )
    durations = cursor.fetchone()
    total_duration = durations['total_duration'] or 0
    avg_duration = durations['avg_duration'] or 0

    cursor.execute(
        "SELECT COUNT(*) AS pending FROM tasks WHERE status='Pending' AND user_id = %s",
        (current_user.id,)
    )
    pending_tasks = cursor.fetchone()['pending'] or 0

    # Chart data — filter by user_id
    cursor.execute(
        "SELECT status, COUNT(*) AS count FROM tasks WHERE user_id = %s GROUP BY status",
        (current_user.id,)
    )
    status_data = cursor.fetchall()

    cursor.execute(
        "SELECT category, COUNT(*) AS count FROM tasks WHERE user_id = %s GROUP BY category",
        (current_user.id,)
    )
    category_data = cursor.fetchall()

    # For categories dropdown
    cursor.execute("SELECT DISTINCT category FROM tasks WHERE user_id = %s", (current_user.id,))
    categories = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks,
        total_duration=round(total_duration, 2),
        avg_duration=round(avg_duration, 2),
        pending_tasks=pending_tasks,
        search_query=search_query,
        categories=categories,
        status_data={
            'labels': [row['status'] for row in status_data],
            'values': [row['count'] for row in status_data]
        },
        category_data={
            'labels': [row['category'] for row in category_data],
            'values': [row['count'] for row in category_data]
        }
    )



# ---------- Toggle Task Status ----------
@app.route('/toggle_status/<int:id>', methods=['POST'])
def toggle_status(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch current status
    cursor.execute("SELECT status FROM tasks WHERE id=%s", (id,))
    current_status = cursor.fetchone()['status']

    # Toggle
    new_status = 'Completed' if current_status == 'Pending' else 'Pending'
    cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (new_status, id))
    conn.commit()

    # Updated chart data
    cursor.execute("SELECT status, COUNT(*) AS count FROM tasks GROUP BY status")
    status_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        'success': True,
        'new_status': new_status,
        'status_data': {
            'labels': [row['status'] for row in status_data],
            'values': [row['count'] for row in status_data]
        }
    })


#add task
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        duration = request.form.get('duration') or 0
        date = request.form.get('date') or None
        status = request.form.get('status') or 'Pending'
        deadline = request.form.get('deadline') or None   # expects YYYY-MM-DD or blank
        progress = request.form.get('progress') or 0
        try:
            progress = int(progress)
            if progress < 0: progress = 0
            if progress > 100: progress = 100
        except ValueError:
            progress = 0

        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = current_user.id
        cursor.execute(
            "INSERT INTO tasks (title, category, duration, date, status, deadline, progress, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (title, category, duration, date, status, deadline, progress, user_id)
        )
        conn.commit()
        conn.close()
        flash("Task added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_task.html')



#Edit task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (id, current_user.id))
    task = cursor.fetchone()

    if not task:
        conn.close()
        flash("Task not found or you don't have permission.", "danger")
        return redirect(url_for('index'))

    if request.method == "POST":
        title = request.form['title']
        category = request.form['category']
        duration = request.form.get('duration') or 0
        date = request.form.get('date') or None
        status = request.form.get('status') or 'Pending'
        deadline = request.form.get('deadline') or None
        progress = request.form.get('progress') or 0
        try:
            progress = int(progress)
            if progress < 0: progress = 0
            if progress > 100: progress = 100
        except ValueError:
            progress = task.get('progress', 0)

        cursor.execute(
            "UPDATE tasks SET title=%s, category=%s, duration=%s, date=%s, status=%s, deadline=%s, progress=%s WHERE id=%s AND user_id=%s",
            (title, category, duration, date, status, deadline, progress, id, current_user.id)
        )
        conn.commit()
        conn.close()
        flash("Task Updated Successfully!", "info")
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_task.html', task=task)


#Delete task:
@app.route("/delete/<int:id>")
def delete_task(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE id = %s",(id, ))
    conn.commit()
    conn.close()
    flash("Task Deleted!", "danger")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)