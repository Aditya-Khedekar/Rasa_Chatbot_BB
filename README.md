# Shipment Assistance Chatbot

This is a **Rasa-based conversational chatbot** designed to assist users with shipment-related queries. It supports tracking shipment status, changing addresses, providing delivery estimates, collecting feedback via a rating system, and summarizing the chat with sentiment analysis using a local LLaMA model.

---

## ✨ Features
- Track shipment using Tracking ID
- Change source and destination pincodes
- Get estimated delivery date
- Star rating system for feedback
- Chat summary and sentiment analysis via Ollama + LLaMA3.2:latest
- Validation of Tracking ID and Pincodes
- User-friendly front-end with buttons and quick replies

---

## ♻ Project Structure
```
.
├── actions/                  # Custom backend logic (Python)
│   └── actions.py            
├── data/                     # Rules and stories for conversation
│   ├── rules.yml             
│   └── stories.yml           
├── models/                   # Trained Rasa models (auto-generated)
├── static/                   # Front-end static assets (images etc.)
├── templates/                # Front-end HTML
│   └── index.html            
├── ratings_log.csv           # CSV mock database of ratings
├── credentials.yml           # Channels configuration
├── domain.yml                # All intents, slots, entities, responses etc.
├── endpoints.yml             # Action server + other services
├── nlu.yml                   # Training data (intents and entities)
├── config.yml                # NLU pipeline and policies
├── README.md                 # This file
└── chat.js                   # Front-end chat logic
```

---

## ⚖️ Prerequisites

- Python 3.8 or above
- [Rasa Open Source](https://rasa.com/docs/rasa/installation/)
- Node.js (for running front-end if needed)
- Git
- Optional: [Ollama](https://ollama.com) (to host LLaMA model locally)

---

## 📚 Setup Instructions

### 1. Clone this Repository
```bash
git clone https://github.com/<your-username>/shipment-chatbot.git
cd shipment-chatbot
```

### 2. Create Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:
```bash
pip install rasa pandas requests
```

---

## ⚙️ Rasa Bot Setup

### 1. Train the Bot
```bash
rasa train
```

### 2. Start the Action Server (custom backend logic)
```bash
rasa run actions
```

### 3. Start the Rasa Server (NLU + Dialogue)
```bash
rasa run --enable-api --cors "*" --debug
```

---

## 🌐 Running the Front-End

Simply open `templates/index.html` in your browser.
Make sure the Rasa server is running at `http://localhost:5005` and the action server at `http://localhost:5055`.

If the chat window doesn’t render properly, you may need to serve the folder using a local HTTP server like:
```bash
python -m http.server 8080
```
Then open `http://localhost:8080/templates/index.html`

---

## 📂 What Each File Does

| File | Description |
|------|-------------|
| `domain.yml` | Defines intents, entities, slots, responses, forms |
| `nlu.yml` | Contains training examples for each intent/entity |
| `rules.yml` | Contains fixed conversation rules |
| `stories.yml` | Contains example conversation flows |
| `config.yml` | NLU pipeline + dialogue policy setup |
| `endpoints.yml` | Action server + optional model server endpoints |
| `actions.py` | All custom backend logic (form validations, API call mocks, summary generation etc.) |
| `ratings_log.csv` | Stores feedback entries from users |
| `chat.js` | Handles frontend rendering, sending/receiving messages, star rating, markdown etc. |

---

## 🔍 Special Features Implemented

- **Form Validation**: Tracking ID must be 9 digits and present in DB. Pincodes must be 6-digit numbers.
- **Button-Based Inputs**: Reduces ambiguity and improves flow.
- **Feedback Collection**: Ratings from 1 to 5 stars stored in `ratings_log.csv`
- **Chat Summary**: Uses LLaMA3.2 via local Ollama server for generating text summary and sentiment.

---

## 🌀 Example Flow
1. User greets the bot.
2. Selects "Track Shipment".
3. Bot asks for Tracking ID and validates it.
4. Bot shows current status.
5. Bot asks if anything else is needed.
6. User gives feedback using star rating.
7. Chat summary and sentiment is shown.

---

## ⚠️ Troubleshooting
- **Empty summary output**: Check if `ratings_log.csv` has at least one complete row.
- **No bot response**: Ensure both Rasa and action server are running.
- **Star rating doesn’t submit**: Check JavaScript errors in browser console.

---

## 🌐 Credits
Developed during internship at **Black Box Navi Mumbai** (June 2025 - July 2025).
Built using open-source technologies: **Rasa**, **Ollama**, **HTML/CSS/JS**.

---

## 📅 Future Improvements
- Connect to live shipment database/API
- Integrate WhatsApp/Telegram as front-end
- Improve fallback and ambiguous intent handling
- Multilingual support

---

## ✅ License
This project is released under the MIT License. Feel free to fork and improve it!
