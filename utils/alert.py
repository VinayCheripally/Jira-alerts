import pyttsx3
from datetime import datetime, timedelta
import threading
from twilio.rest import Client
from dotenv import load_dotenv
import os 
from utils.popup import popup_window_with_timeout
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv() 

smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = os.getenv("SENDER_EMAIL")
password = os.getenv("PASSWORD")


def reminder(data,email,days):
    today_date = datetime.today().date()
    end_date = (datetime.now() + timedelta(days)).date()
    engine = pyttsx3.init()
    def speak_message(text):
        engine.say(message)
        engine.runAndWait()
    for board in data:
        for task in data[board]:
            if task['duedate']:
                task_due_date = datetime.strptime(task['duedate'], '%Y-%m-%d').date()
                if today_date <= task_due_date <= end_date:
                    message = f"Reminder: You have a task due at {task['duedate']}. Task {task['key']} - {task['summary']}."
                    threading.Thread(target=speak_message,args=(message,)).start()
                    if not popup_window_with_timeout(message):
                        subject = 'Reminder email for task due in Jira'
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = email
                        msg['Subject'] = subject
                        msg.attach(MIMEText(message, 'plain'))
                        try:
                            server = smtplib.SMTP(smtp_server, smtp_port)
                            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                            server.login(sender_email, password)  # Login to the email account
                            server.send_message(msg)  # Send the email
                        except Exception as e:
                            print(e)
                    
