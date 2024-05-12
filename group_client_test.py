import secrets
import smtplib
import string
import threading
from tkinter import filedialog as fd
from datetime import datetime
import customtkinter
import pyotp
from ttkbootstrap.scrolled import ScrolledFrame
import re
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk
import tkinter as tk
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

from GUI.HomePage import HomePage


class TwoFactorAuthentication(CTkToplevel):
    def __init__(self, master, email):
        super().__init__(master)
        self.master = master
        self.email = email
        self.email = email

        self.verification_pass = self.send_email(self.email)
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
        entered_code = "".join(entry.get() for entry in self.code_entries)
        if entered_code == self.verification_pass:
            print("Verification successful")
        else:
            print("Verification failed")

    def create_verification_code(self):
        key = "TomerBenShushanSecretKey"

        totp = pyotp.TOTP(key)
        print(totp)
        return totp.now()
    def send_email(self, u_email):
        # Generate a random password of the specified length
        password = self.create_verification_code()
        try:
            # Create a MIME multipart message
            msg = MIMEMultipart()
            msg['From'] = 'cloudav03@gmail.com'
            msg['To'] = u_email
            msg['Subject'] = 'Two-Factor Authentication'

            # Read HTML content from file
            with open('GUI/2fa mail.html', 'r') as file:
                html_content = file.read()

            # Replace placeholders with actual data
            html_content = html_content.replace('[Client Name]', 'John Doe')
            html_content = html_content.replace('[Client Location]', 'New York')
            html_content = html_content.replace('[Client IP]', '192.168.1.1')
            html_content = html_content.replace('[Client Device]', 'Desktop')
            html_content = html_content.replace('[Client Time]', '2024-05-10 12:00:00')
            html_content = html_content.replace('[Client Code]', password)

            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Attach the logo image
            img_path = "GUI/file_icons/logo_cloudav_2.png"
            with open(img_path, 'rb') as f:
                logo_image = MIMEImage(f.read())
                logo_image.add_header('Content-ID', '<logo>')
                msg.attach(logo_image)

            # Connect to SMTP server and send email
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login('cloudav03@gmail.com', 'ivdr wron fhzc xjgo')
            server.sendmail('cloudav03@gmail.com', u_email, msg.as_string())
            server.quit()

            print("Email sent successfully!")

            return password
        except Exception as e:
            print(e)
            print("Email failed to send.")


def run_test(email):
    root = tk.Tk()

    # Create an instance of TwoFactorAuthentication with the provided email address
    two_factor_auth = TwoFactorAuthentication(root, email)

    # Run the Tkinter main loop
    root.mainloop()


# Run the test with the provided email address
if __name__ == "__main__":
    email = "cajoya9761@bsomek.com"  # Provide the email address here
    run_test(email)
