Smart Calendar Agent AI 

Modern AI-Powered Calendar Management & Productivity Assistant built with Flask, Google Calendar API and Ollama AI.

Smart Calendar Agent AI helps users manage meetings, protect focus time, reduce burnout risk, analyze productivity trends and interact with their calendar through an AI Copilot assistant.

⸻

Overview

Smart Calendar Agent AI is an intelligent productivity platform designed to transform Google Calendar into a smart personal assistant.

The platform combines:

* Google Calendar Integration
* AI Productivity Analysis
* Burnout Detection
* Focus Time Planning
* AI Copilot Assistant
* Calendar Analytics
* Smart Recommendations
* Modern SaaS-Style Dashboard

The goal is to help users maintain a healthy balance between meetings, focus work and productivity.

⸻

Key Features 

AI Copilot Assistant

* ChatGPT-style AI interface
* Powered by local Ollama AI
* Understands calendar context
* Answers productivity questions
* Provides personalized recommendations
* Can help users manage calendar actions

Google Calendar Integration

* Secure OAuth Login
* Real-time Calendar Sync
* Read Calendar Events
* Create New Events
* Create Focus Blocks
* Edit Events
* Delete Events

Burnout Risk Analysis

* Meeting Load Analysis
* Focus Time Tracking
* Burnout Score Calculation
* Burnout Level Classification
* AI-Powered Recommendations

Focus Time Planner

* Create Focus Blocks
* Deep Work Protection
* Smart Scheduling
* Productivity Optimization

Analytics Dashboard

* Weekly Event Analytics
* Focus Time Analytics
* Burnout Trends
* Productivity Metrics
* Interactive Charts

Smart Recommendations

* AI-generated productivity advice
* Burnout prevention suggestions
* Focus improvement recommendations
* Calendar optimization insights

Modern SaaS UI

* Responsive Design
* Dark Mode
* Light Mode
* Premium Dashboard
* Workspace Center
* AI Workspace Settings
* Clean Portfolio-Ready Interface

⸻

Screenshots 

Dashboard
<img src="screenshots/Dashboard.png" width="900">
⸻

Calendar
<img src="screenshots/Calendar.png" width="900">
⸻

Meetings
<img src="screenshots/Meeting.png" width="900">
⸻

AI Insights
<img src="screenshots/AI-Insights.png" width="900">
⸻

AI Recommendations
<img src="screenshots/Recommendations.png" width="900">
⸻

Copilot Chat
<img src="screenshots/Chat.png" width="900">
⸻

Analytics & Charts
<img src="screenshots/Charts.png" width="900">
⸻

Technology Stack 

Backend

* Python
* Flask
* Google Calendar API
* OAuth 2.0

AI Layer

* Ollama
* Local AI Model
* Local AI Processing

Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

Visualization

* Chart.js

⸻

Project Architecture

Smart-Calendar-Agent-AI/
│
├── app.py
├── config.py
├── auth.py
├── analytics.py
├── calendar_utils.py
├── ollama_ai.py
│
├── templates/
│   ├── index.html
│   ├── calendar.html
│   ├── meetings.html
│   ├── focus.html
│   ├── ai_insights.html
│   ├── analytics.html
│   ├── copilot.html
│   └── settings.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│
├── screenshots/
│   ├── Dashboard.png
│   ├── Calendar.png
│   ├── Meeting.png
│   ├── AI-Insights.png
│   ├── Recommendations.png
│   ├── Chat.png
│   └── Charts.png
│
├── requirements.txt
├── README.md
└── .gitignore

⸻

Configuration 

This project does not include personal API keys, OAuth secrets or private credentials.

Each user must create and add their own Google Calendar API credentials before running the application.

Google Calendar API Setup

1. Go to Google Cloud Console.
2. Create a new project.
3. Enable Google Calendar API.
4. Create OAuth 2.0 credentials.
5. Download the credentials file.
6. Add the credentials file to the project locally.

Example local structure:

Smart-Calendar-Agent-AI/
│
├── credentials.json
├── app.py
├── config.py
└── ...

The credentials file should not be pushed to GitHub.

⸻

Environment Variables

Create a .env file in the project root and add your own values.

Example:

SECRET_KEY=your_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=your_google_redirect_uri

Never commit .env files to GitHub.

⸻

Ollama Setup 

Install Ollama locally and download any supported local model.

Example:

ollama pull llama3.2

You can use any compatible Ollama model depending on your hardware and requirements.

⸻

Installation Guide macOS 

Clone Repository

git clone https://github.com/baseetnaseri6/Smart-Calendar-Agent-AI.git
cd Smart-Calendar-Agent-AI

Create Virtual Environment

python3 -m venv .venv

Activate Virtual Environment

source .venv/bin/activate

Install Dependencies

pip install -r requirements.txt

Run Application

python app.py

Then open the local application in your browser.

⸻

Installation Guide Windows 

Clone Repository

git clone https://github.com/baseetnaseri6/Smart-Calendar-Agent-AI.git
cd Smart-Calendar-Agent-AI

Create Virtual Environment

python -m venv .venv

Activate Environment

.venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Run Application

python app.py

Then open the local application in your browser.

⸻

Security Notes 

This repository should not contain private credentials.

Do not commit:

.env
credentials.json
client_secret.json
token.json
API keys
OAuth secrets
Local tokens
Private configuration files

Recommended .gitignore entries:

.env
credentials.json
client_secret.json
token.json
.venv/
venv/
__pycache__/
*.pyc
.vscode/
.DS_Store
*.log

⸻

AI Capabilities 

The platform uses local AI through Ollama to:

* Analyze meeting schedules
* Detect burnout risk
* Generate productivity insights
* Provide calendar recommendations
* Answer user questions through Copilot
* Help users plan focus time and improve productivity

All AI processing can run locally using user-provided Ollama setup.

⸻

Future Roadmap 

Planned features:

* Smart Meeting Scheduler
* AI Task Manager
* Automatic Focus Time Optimization
* Email Integration
* PDF Productivity Reports
* Team Workspace Support
* Multi-Calendar Support
* Mobile Application
* Advanced AI Planning Agent
* Free Time Finder
* Smart Focus Planner

⸻

Why This Project?

Modern professionals spend a large portion of their day managing calendars, meetings and tasks.

Smart Calendar Agent AI was created to transform a traditional calendar into an intelligent productivity assistant that helps users:

* Protect focus time
* Reduce meeting overload
* Prevent burnout
* Improve productivity
* Make better scheduling decisions

⸻

Author

Mohammad Baseet Naseri

AI • Data Science • Automation • Software Development

⸻

License

This project is licensed under the MIT Licens