# Jira Alerts

This is a project where you can get alerts for the issues in Jira.

---

## Features

- While reminding you it will use a library which turns text into voice and also it pops up a window with a 'got it' button and if you don't press it in ten seconds it will send a message to your phone.

---

## Installation

### Prerequisites

- Python

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/VinayCheripally/Jira-alerts.git
   cd Jira-alerts
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   Create a .env file with the following variables
   ```bash
   TWILIO_ACCOUNT_SID=<Your Twilio Account SID>
   TWILIO_AUTH_TOKEN=<Your Twilio Auth Token>
   TWILIO_SENDER=<Twilio Sender Number>
   TWILIO_RECEIVER=<Your Phone Number>
   CLIENT_ID=<Atlassian application Client ID>
   CLIENT_SECRET=<Atlassian application Client Secret>
   SECRET_KEY=<Strong secret key>
   ```
4. Run the program
   ```bash
   python app.py
   ```
