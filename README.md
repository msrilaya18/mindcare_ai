# 🧠 MindCare AI — Mental Health Support Chatbot

> An AI-powered mental health web application using Flask and OpenAI GPT. Fully anonymous — no data stored.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3-green?style=flat-square&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub%20Actions-blue?style=flat-square&logo=github)

---

## 📁 Project Structure

```
mindcare-ai/
├── app.py                          # Flask backend + OpenAI logic
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container definition
├── .github/workflows/python-app.yml # GitHub Actions CI/CD
├── .flake8                         # Linting config
├── .gitignore
├── .dockerignore
├── .env.example                    # Env variable template
├── templates/
│   └── index.html                  # Frontend UI (Bootstrap 5)
├── static/
│   ├── css/style.css               # Premium styles
│   └── js/script.js                # Frontend logic
└── tests/
    └── test_app.py                 # pytest test suite
```

---

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd mindcare-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
```
Open `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
FLASK_DEBUG=1
```

### 3. Run the Application
```bash
python app.py
```
Open your browser at → **http://localhost:5000**

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run linting
flake8 .
```

---

## 🐳 Docker

```bash
# Build image
docker build -t mindcare-ai .

# Run container (pass your API key)
docker run -p 5000:5000 -e OPENAI_API_KEY=sk-your-key mindcare-ai
```

---

## 🔁 CI/CD Pipeline

| Tool | Purpose |
|---|---|
| **flake8** | Code linting |
| **pytest** | Automated testing |
| **Docker** | Containerization |
| **GitHub Actions** | CI/CD pipeline |

Pipelines run automatically on every push/PR on `main` or `develop`.

---

## 🌿 SCM — Suggested Git Commit Messages

```bash
# Initial setup
git commit -m "feat: initial project structure and Flask app setup"

# After adding OpenAI integration
git commit -m "feat: integrate OpenAI API with stress classification logic"

# After adding frontend
git commit -m "feat: add premium dark mode UI with glassmorphism design"

# After tests
git commit -m "test: add pytest suite with 6 test cases and mocking"

# After Docker
git commit -m "chore: add Dockerfile and .dockerignore for containerization"

# After CI/CD
git commit -m "ci: add Bitbucket Pipelines and GitHub Actions workflow"

# Bug fixes
git commit -m "fix: handle JSON decode error from OpenAI response"

# Documentation
git commit -m "docs: add README with setup, usage and commit guidelines"
```

---

## 🔒 Privacy

- **No database** — conversations are never stored
- **Anonymous** — no user identification
- **Ephemeral** — each session is fully independent

---

## ⚠️ Disclaimer

MindCare AI provides supportive guidance only. It is **not a substitute** for professional mental health care. In emergencies, please contact your local emergency services.

---

## 📞 Helplines (India)

| Organization | Number |
|---|---|
| iCall | 9152987821 |
| Vandrevala Foundation | 1860-2662-345 |
| NIMHANS | 080-46110007 |
