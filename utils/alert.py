import pyttsx3
from datetime import datetime, timedelta
import threading
from twilio.rest import Client
from dotenv import load_dotenv
import os 
from utils.popup import popup_window_with_timeout

load_dotenv() 
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_sender = os.getenv("TWILIO_SENDER")
twilio_receiver = os.getenv('TWILIO_RECEIVER')

client = Client(account_sid, auth_token)

tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

def reminder(data):
    engine = pyttsx3.init()
    def speak_message(text):
        engine.say(message)
        engine.runAndWait()
    for board in data:
        for task in data[board]:
            if task['duedate'] and task['duedate'] == tomorrow_date:
                message = f"Reminder: You have a task due tomorrow. Task {task['key']} - {task['summary']}."
                threading.Thread(target=speak_message,args=(message,)).start()
                if not popup_window_with_timeout(message):
                    m = client.messages.create(
                    body=message, 
                    from_=twilio_sender,  
                    to=twilio_receiver   
                    )
