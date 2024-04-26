import secrets
import smtplib
import string
import threading
from tkinter import filedialog as fd
from datetime import datetime
import customtkinter
from ttkbootstrap.scrolled import ScrolledFrame
import re
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk
import tkinter as tk

from GUI.HomePage import HomePage


class TwoFactorAuthentication(CTkToplevel):
    def __init__(self, master, email, client_name, client_ip):
        super().__init__(master)
        self.master = master
        self.email = email
        self.client_name = client_name
        self.client_ip = client_ip

        self.verification_pass = self.send_email(self.email, self.client_name, self.client_ip)
        self.setup_image()
        self.setup_information()
        self.setup_verification_code_frame()
        self.setup_submit_button()

    def setup_image(self):
        container = tk.Frame(master=self)
        container.pack(side="top", padx=20)
        two_fa_image = CTkImage(
            light_image=Image.open(r"GUI\file_icons\2fa_image.jpg"),
            dark_image=Image.open(r"GUI\file_icons\2fa_image.jpg"),
            size=(251, 173)
        )
        image_label = CTkLabel(container, image=two_fa_image, text="", bg_color='transparent')
        image_label.pack(side="top", fill="both", expand=True)

    def setup_information(self):
        container = CTkFrame(master=self)
        container.pack(side="top", fill="both", padx=20)
        CTkLabel(container, text="Two-Factor\nAuthentication", font=("Arial Bold", 30), bg_color='transparent').pack(
            side="top", anchor="center", pady=30)
        CTkLabel(container, text="Enter the six-digit code we have sent to your email", font=("Helvetica", 12),
                 bg_color='transparent').pack(side="top",
                                              anchor="center", pady=10)

    def setup_verification_code_frame(self):
        code_frame = CTkFrame(self)
        code_frame.pack(side="top", fill="both", padx=20, pady=20, expand=True)

        self.code_entries = []
        for i in range(6):
            digit_entry = CTkEntry(code_frame, width=50, height=50, font=("Helvetica", 20), justify="center")
            digit_entry.pack(side="left", padx=15, expand=True)

            # Bind the <Key> event to move the focus to the next digit_entry widget
            digit_entry.bind('<Key>', lambda event, entry=digit_entry, index=i: self.on_key(event, entry, index))

            self.code_entries.append(digit_entry)

    def on_key(self, event, entry, index):
        if event.char.isdigit() and index < 5:
            self.code_entries[index + 1].focus_set()

    def setup_submit_button(self):
        container_frame = CTkFrame(self)
        container_frame.pack(side="bottom", fill="both", padx=20, pady=20)
        submit_button = CTkButton(container_frame, text="Verify", command=self.on_submit, font=("Helvetica", 20))
        submit_button.pack(side="top", pady=10, anchor="center", fill='x', padx=10)

        self.answer_label = CTkLabel(container_frame, text="", text_color="red")

    def on_submit(self):
        if self.code_entries == self.verification_pass:
            print("gay")

    def send_email(self, u_email, client_name, client_ip):
        characters = string.digits

        # Generate a random password of the specified length
        password = ''.join(secrets.choice(characters) for i in range(6))
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login('cloudav03@gmail.com', 'ivdr wron fhzc xjgo')

            # HTML content for the email message with placeholders for dynamic data
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Two-Factor Authentication</title>
                <style>
                    /* Styles for the email content */
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f6f6f6;
                        color: #333;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 700px; /* Adjusted max-width for wider container */
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #1e88e5;
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    h2 {{
                        color: #4caf50;
                        text-align: left;
                    }}
                    p {{
                        margin-bottom: 20px;
                        color: #666;
                        line-height: 1.6;
                    }}
                    .code-input {{
                        width: 100px;
                        padding: 10px;
                        font-size: 16px;
                        text-align: center;
                        border: 2px solid #1e88e5;
                        border-radius: 5px;
                        color: #1e88e5;
                        margin-bottom: 20px;
                        display: inline-block;
                    }}
                    .logo {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 0 auto 30px;
                    }}
                    .cta-button {{
                        background-color: #4caf50;
                        color: #fff;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                    }}
                    .cta-button:hover {{
                        background-color: #388e3c;
                    }}
                    .small-msg {{
                        font-size: 12px;
                        color: #999;
                        text-align: center;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <img src="GUI/file_icons/logo_cloudav_2.png" class="logo" alt="CloudAV Logo">
                    <h1>Two-Factor Authentication</h1>
                    <h2>Dear {},</h2>
                    <p>We noticed a login from a new device or location for YeledYafe12 and want to make sure it was you.</p>
                    <p><strong>Regional Location:</strong> Tel Aviv, Israel<br>
                    <strong>IP Address:</strong> {}<br>
                    <strong>Device:</strong> Computer (Windows)<br>
                    <strong>Time:</strong> {}</p>
                    <p>To enhance the security of your account, we've introduced Two-Factor Authentication (2FA). This added layer of protection requires you to input a unique 6-digit code during login. The code will be sent to your registered email or phone number.</p>
                    <p>Please find the space below to input the 6-digit code:</p>
                    <div class="code-input">{}</div>
                    <p>Your account's security is our priority, and we appreciate your cooperation in keeping it secure.</p>
                    <p>Best regards,<br>CloudAV</p>
                    <p class="small-msg"><br>Please do not reply to this message as the response will not be delivered to the originator.</p>
                </div>
            </body>
            </html>
            """.format(client_name, client_ip, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), password)

            # Create a MIMEText object with HTML content
            from email.mime.text import MIMEText
            message = MIMEText(html_content, 'html')

            message['Subject'] = 'Two-Factor Authentication'
            message['From'] = 'cloudav03@gmail.com'
            message['To'] = u_email

            server.sendmail('cloudav03@gmail.com', u_email, message.as_string())
            print("Email sent successfully!")

            return password
        except Exception as e:
            print(e)
            print("Email failed to send.")


def run_test():
    root = tk.Tk()
    client_name = "John Doe"
    client_ip = "192.168.1.1"
    email = "chairgood1@gmail.com"

    # Create an instance of TwoFactorAuthentication
    two_factor_auth = TwoFactorAuthentication(root, client_name, client_ip, email)

    # Run the Tkinter main loop
    root.mainloop()


# Run the test
if __name__ == "__main__":
    run_test()
