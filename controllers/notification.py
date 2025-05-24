class Notification():

    # Send batch message
    def send_notification(channels):
        for channel, message in channels:
            getattr(Notification, f'send_{channel}_notification')(message)

    def send_email_notification(message):
        # Handle code send message to mail provider
        print(f"[EMAIL] {message}")

    def send_application_notification(message):
        # Handle code push message to firebase/APNS/SQS
        print(f"[Application] {message}")

    def send_sms_notification(message):
        # Handle code send message to sms provider
        print(f"[SMS] {message}")
