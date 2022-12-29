from fastapi_mail import MessageSchema, FastMail
from starlette.background import BackgroundTasks

from config import email_conf


async def send_email(recipients: list, template_name: str, context: dict, subject: str):

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context
    )

    fm = FastMail(email_conf)
    BackgroundTasks().add_task(fm.send_message, message, template_name=template_name)
