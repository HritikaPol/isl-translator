# 📊 Multilingual ISL Translator & Analytics Dashboard

A cloud-deployed full-stack web application that converts multilingual text (English & Marathi) into Indian Sign Language (ISL) gesture representations, with built-in user authentication and translation analytics dashboard.

🔗 **Live Demo:** https://isl-translator-z2ke.onrender.com  
💻 **GitHub:** https://github.com/HritikaPol/isl-translator  

---

## 🚀 Project Overview

This project bridges communication accessibility gaps by translating user-entered text into ISL gesture images.

In addition to translation, the platform logs user interactions and generates analytical insights through an interactive dashboard.

The system is fully deployed on the cloud using production-level deployment practices.

---

## 🔐 Core Features

### User Authentication
- Secure signup & login
- Password validation rules:
  - Minimum 8 characters
  - At least 4 letters
  - At least 3 numbers
  - At least 1 special character
- Password hashing using bcrypt
- Session-based authentication

### Multilingual ISL Translation
- English (ALL CAPS) support
- Marathi character support
- Character-to-gesture mapping
- Real-time visual output

### 📈 Analytics Dashboard
- Logs every translation event
- SQL-based aggregation queries
- KPIs displayed:
  - Total translations
  - Unique users
  - Average translations per user
  - Most active users
- Visualizations:
  - Daily trend (Line chart)
  - Top users (Bar chart)
  - Character frequency (Doughnut chart)

### ☁ Deployment
- Hosted on Render
- Production server using Gunicorn
- Version controlled via Git & GitHub
- Auto-deploy enabled

---

## 🛠 Tech Stack

**Backend**
- Python
- Flask
- SQLite
- Flask-Bcrypt

**Frontend**
- HTML
- Bootstrap 5
- JavaScript
- Chart.js

**Deployment**
- Render
- Gunicorn

---

## 🧠 Data & Analytics Design

The system captures translation logs in a relational database and performs SQL aggregation to generate:

- Usage trends
- User activity ranking
- Character frequency analysis
- KPI metrics

This demonstrates:
- Database schema design
- SQL grouping & aggregation
- Data-driven insight extraction
- Interactive dashboard visualization

---

## 📂 Database Schema

### Users
- id (Primary Key)
- username (Unique)
- password (Hashed)

### Translations
- id (Primary Key)
- username
- input_text
- timestamp

---

## ▶ Run Locally

```bash
git clone https://github.com/HritikaPol/isl-translator.git
cd isl-translator
pip install -r requirements.txt
python app.py

## 📸 Screenshots

### Login Page
![Login](static/screenshots/login.png)

### Translation Interface
![Translator](static/screenshots/translator.png)

### Analytics Dashboard
![Dashboard](static/screenshots/dashboard.png)