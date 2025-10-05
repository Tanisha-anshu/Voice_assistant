# Multilingual Hotel Reservation Voice Assistant

An AI-powered voice-based multilingual hotel reservation assistant built using LiveKit Agents, Google Gemini Realtime API, and Google Sheets.

This assistant can:

-Understand English, Hindi, and Hinglish voice commands

-Interpret natural language dates like “next Friday” or “15 October”

-Check room availability and create bookings in Google Sheets

-Converse naturally with users in their preferred language


Built for realtime, low-latency interaction — just like talking to a real hotel receptionist!

# Features

Multilingual voice assistant (English / Hindi / Hinglish)

Google Sheets integration for storing bookings

Natural date understanding (e.g., “next Friday”)

Uses LiveKit Agents for real-time voice processing

Fully customizable instructions & tools

Built with Gemini Realtime API for intelligent conversations

Project Structure

Voice Assistant/
│

├── agent_main.py          # Core LiveKit Agent logic

├── booking_tools.py       # Functions to check and create bookings

├── prompts.py             # LLM instructions and conversation flow

├── sheets.py              # (Sheet helper for Google Sheets)

├── requirements.txt       # All required dependencies

├── .env                   # API keys and LiveKit credentials

└── README.md              


# Setup Instructions

1️⃣ Create & Activate Virtual Environment

python -m venv .venv

.venv\Scripts\activate      # On Windows

or

source .venv/bin/activate   # On Mac/Linux


2️⃣ Install Dependencies

pip install -r requirements.txt


3️⃣ Configure Environment Variables

Create a .env file in the root directory and add:

LIVEKIT_URL=<your_livekit_url>

LIVEKIT_API_KEY=<your_livekit_api_key>

LIVEKIT_API_SECRET=<your_livekit_api_secret>

GOOGLE_API_KEY=<your_google_api_key>

SPREAD_SERVICE_ACCOUNT_JSON=service_account.json

BOOKINGS_SHEET_ID=<11C3xHRUI0G-O0yjJbt9KPkCuSDw5AJFnIAmxNy>

BOOKINGS_WORKSHEET_NAME=bookings

GMAIL_USER=<example@gmail.com>

GMAIL_APP_PASSWORD=<Ans123>


If using Google Sheets:

Place your service account JSON key file in the same folder (e.g. service_account.json)
Share your Google Sheet with the service account email address


4️⃣ Run the Assistant (Console Mode)

python agent_main.py console

Press Ctrl + B to toggle between text and audio input.

Press Q to quit.

Run the Assistant (development Mode)

python agent_main.py dev

Connect with Livekit Playground and start using the assistant.


# Example Conversation

User: “Namaste, mujhe agle Friday ke liye room book karna hai.”

Assistant: “Namaste ji! Zaroor  Aapka check-in date hoga 2025-10-10. Check-out kab karna chahengi?”

User: “Sunday tak.”

Assistant: “Okay ji, confirm kar du? Check-in: 2025-10-10, Check-out: 2025-10-12.”

User: “Yes.”

Assistant: “Congrats! Aapki booking confirm hai from 10th to 12th October.”
