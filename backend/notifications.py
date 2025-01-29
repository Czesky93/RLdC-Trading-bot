import smtplib

def send_email_notification(to_email, subject, message):
    server = smtplib.SMTP("smtp.example.com", 587)
    server.starttls()
    server.login("your_email@example.com", "your_password")
    msg = f"Subject: {subject}\n\n{message}"
    server.sendmail("your_email@example.com", to_email, msg)
    server.quit()
