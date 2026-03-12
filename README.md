# Leave Management System

A web-based Leave Management System built using Flask and SQLAlchemy.  
This application allows employees to apply for leave and managers to approve or reject requests.

## 🚀 Features
- User login system
- Apply for different types of leave
- Leave balance tracking
- Manager dashboard for approval/rejection
- Leave history tracking
- Secure authentication

## 🛠️ Technologies Used
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Login
- HTML
- CSS

## 📂 Project Structure

leave-management-system  
│  
├── app.py  
├── config.py  
├── models.py  
├── database.db  
│  
├── templates  
│ ├── login.html  
│ ├── dashboard.html  
│ ├── apply_leave.html  
│ ├── manager.html  
│ └── history.html  
│  
└── static  
   └── style.css  

## ⚙️ Installation

1. Clone the repository
```
git clone https://github.com/yourusername/leave-management-system.git
```

2. Install dependencies
```
pip install flask flask_sqlalchemy flask_login werkzeug
```

3. Run the application
```
python app.py
```

4. Open in browser
```
http://127.0.0.1:5000/login
```

## 🔑 Default Login Credentials

Manager
```
username: manager
password: manager123
```

Employee
```
username: emp1
password: emp123
```

## 🌐 Live Demo
https://leave-management-system-16n7.onrender.com/login

## 📌 Future Improvements
- Email notifications for leave approval
- Admin dashboard
- Better UI design
- Role-based access control

⭐ If you like this project, feel free to give it a star!
