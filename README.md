# 🚀 Productivity Dashboard — Flask Web Application

A powerful **Productivity Management Dashboard** built using **Flask**, **MySQL**, and **Bootstrap 5**.  
It helps users efficiently manage their daily tasks, track productivity, and visualize progress through interactive analytics and visual charts.  

This full-stack web app demonstrates practical implementation of **CRUD operations**, **user authentication**, and **data visualization**, all integrated seamlessly in a modern responsive UI.

---

## 🧠 Features

### 🧍‍♂️ User Authentication
- Secure **Register / Login / Logout** using Flask-Login  
- Passwords safely stored with **Werkzeug hashing**  
- User-specific task storage (isolated dashboards)  

### ✅ Task Management
- Add, edit, delete, and view tasks  
- Filter tasks by **status** or **category**  
- Toggle task completion with circular checkboxes  
- Real-time updates reflected in dashboard charts  

### 🔍 Search & Filtering
- Search tasks by title, category, or status  
- Filter easily with dropdown menus  

### 📊 Analytics Dashboard
- Interactive **Pie** and **Bar Charts** powered by **Chart.js**  
- Displays:  
  - Total Duration ⏱️  
  - Average Duration 📈  
  - Pending Tasks 🕒  

### 👤 Profile & Settings
- Update username, email, and password securely  
- Upload a **profile image**, displayed in the navbar  
- Beautiful **profile dashboard layout**  

### ⚡ Flash Messages & Feedback
- Informative alerts using Flask’s `flash()`  
- Styled via Bootstrap for consistent UX  

### 💅 Responsive & Modern UI
- Built using **Bootstrap 5**  
- Clean typography, centered charts, and dynamic progress bars  

---

## 🧰 Tech Stack

| Layer | Technology | Description |
|-------|-------------|-------------|
| **Backend** | 🐍 Flask | Lightweight Python web framework |
| **Database** | 🗄️ MySQL | Stores users, tasks, and analytics data |
| **ORM / DB Access** | mysql.connector | Direct SQL queries for full control |
| **Frontend** | 💅 HTML5, CSS3, Bootstrap 5 | Responsive, elegant design |
| **Charts** | 📊 Chart.js | Data visualization for tasks |
| **Auth & Security** | 🔐 Flask-Login, Werkzeug | Session handling and password hashing |
| **File Handling** | 🖼️ secure_filename | For secure user profile image uploads |
| **Icons** | 🎨 Bootstrap Icons | For task actions and UI elements |

---

## 🧩 Project Structure

productivity_dashboard/
│
├── app.py # Main Flask application
│
├── templates/ # HTML Templates (Jinja2)
│ ├── index.html # Dashboard + Charts
│ ├── add_task.html # Add new task
│ ├── edit_task.html # Edit existing task
│ ├── login.html # User login
│ ├── register.html # User signup
│ └── profile.html # Profile settings
│
├── static/
│ ├── uploads/ # User profile images
│ ├── css/ # Custom styles
│ └── js/ # Chart.js scripts
│
├── requirements.txt # Dependencies list
├── .gitignore
└── README.md # Project documentation


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/RahulKumarSahDepp/productivity_dashboard.git
cd productivity_dashboard
```

### 2️⃣ Create Virtual Environment
```bash
conda create -n flask_dashboard python=3.12
conda activate flask_dashboard
```
###3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

###4️⃣ Configure Database

```bash
CREATE DATABASE productivity_dashboard;
USE productivity_dashboard;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255)
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    category VARCHAR(100),
    duration FLOAT,
    date DATE,
    status VARCHAR(50),
    deadline DATE,
    progress INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

```

###5️⃣ Run the Application
```bash
flask run
```


⭐ If you like this project, don’t forget to star the repo! ⭐

---

## 🧩 **requirements.txt**

```txt
Flask==3.0.3
Flask-Login==0.6.3
Werkzeug==3.0.3
mysql-connector-python==9.0.0
Jinja2==3.1.4
itsdangerous==2.2.0
click==8.1.7
MarkupSafe==3.0.2
```
