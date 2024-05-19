import os
from datetime import datetime

from pydantic import EmailStr


async def send_confirmation_code(email: EmailStr, code: str):
    # Create a directory to store emails if it doesn't exist
    email_dir = "sent_emails"

    if not os.path.exists(email_dir):
        os.makedirs(email_dir)

    # Generate a unique filename
    email_filename = email.replace(".", "_")
    filename = (
        f"Email_to_{email_filename}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    )

    # Write the email content to a file
    filepath = os.path.join(email_dir, filename)
    with open(filepath, "w") as file:
        file.write("Subject: Confirmation code for token:\n\n")
        file.write(f"Your confirmation code is: {code}")
