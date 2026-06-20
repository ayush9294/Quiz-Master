# 🧠 Quiz Master – Online Quiz Platform

A multi-category quiz platform with timed rounds, score tracking, and a live leaderboard.

## Features
- 4 categories: Python, Web Dev, SQL, General Knowledge
- 15-second countdown timer per question
- Live leaderboard (best scores per user/category)
- Personal score history
- User authentication (register/login)
- 20 pre-seeded questions in SQLite

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript (Fetch API)
- **Backend:** Python (Flask)
- **Database:** SQLite

## Setup & Run

```bash
# 1. Install dependencies
pip install flask

# 2. Run the app (DB auto-created with seed questions)
python app.py

# 3. Open in browser
http://localhost:5000
```

## Project Structure
```
quiz-master/
├── app.py               # Flask backend, routes, SQLite
├── quiz.db              # Auto-created on first run
├── templates/
│   ├── index.html       # Main quiz UI
│   ├── login.html
│   └── register.html
└── static/
    └── style.css
```
