import google.generativeai as genai
from flask import Flask, request, jsonify
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client
import threading
import requests
from flask_cors import CORS
import os
from config import (
    GOOGLE_API_KEY, TO_EMAIL, FROM_EMAIL, SMTP_SERVER, SMTP_PORT,
    SMTP_USER, SMTP_PASSWORD, TO_PHONE_NUMBER, FROM_PHONE_NUMBER,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
)

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})


def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password,
               attachment_data=None, attachment_filename="attachment.jpg"):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_data:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
        msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_sms(to_phone_number, from_phone_number, body, twilio_account_sid, twilio_auth_token):
    client = Client(twilio_account_sid, twilio_auth_token)
    try:
        message = client.messages.create(
            body=body,
            from_=from_phone_number,
            to=to_phone_number
        )
        print(f"SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")


@app.route('/upload', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})

    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({'error': 'No selected file'})

    temp_image_path = "./temp_image.jpg"
    image_file.save(temp_image_path)

    sample_file = genai.upload_file(path=temp_image_path, display_name="Sample Image")
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {file.uri}")

    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    response = model.generate_content(
        [
            "Analyze the given image and determine if it contains a human, an animal, unidentified or is_nothing. Provide the output in JSON format with three keys: 'is_human', 'is_animal', 'unidentified', 'is_nothing'. Each key should have a binary value: 1 for true, 0 for false",
            sample_file]
    )

    print(response)

    send_default_alert = False
    detection_type = ""

    if response.candidates:
        candidates = response.candidates
        for candidate in candidates:
            parts = candidate.content.parts
            for part in parts:
                text = part.text.strip()
                print(text)
                if text.startswith("```json") and text.endswith("```"):
                    text = text[7:-3].strip()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError: {e}")
                    send_default_alert = True
                    continue

                is_human = data.get('is_human')
                unidentified = data.get('unidentified')

                if is_human is not None or unidentified is not None:
                    if is_human == 1:
                        detection_type = "human"
                    elif unidentified == 1:
                        detection_type = "unidentified"

                    body = f"A '{detection_type}' has been detected in the image."
                    subject = f"{detection_type} Detected Alert"
                    send_email(subject, body, TO_EMAIL, FROM_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
                               attachment_data=temp_image_path)
                    send_sms(TO_PHONE_NUMBER, FROM_PHONE_NUMBER, body, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                else:
                    print("Response data does not contain 'is_human' or 'unidentified' keys.")
                    send_default_alert = True
    else:
        print("Response does not contain any candidates.")
        send_default_alert = True

    if send_default_alert:
        body_default = "The image analysis could not determine the presence of a human or animal. Please check the system."
        send_email("Detection Alert", body_default, TO_EMAIL, FROM_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER,
                   SMTP_PASSWORD, attachment_data=temp_image_path)
        send_sms(TO_PHONE_NUMBER, FROM_PHONE_NUMBER, body_default, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    return jsonify({'message': 'Processing done'}), 200


if __name__ == "__main__":
    app.run(port=6754)
