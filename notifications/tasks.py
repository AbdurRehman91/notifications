import logging
from app_platform.celery import app
from .utils import SmsSender,send_push_notification
logger = logging.getLogger(__name__)

@app.task
def send_sms(phone_number, message, priority=False):
    """
    Sends sms to the given phone_number
    Parameters
    ----------
    phone_number: str
        phone number of the user
    message: str
        text to send
    priority: bool
        to prioritize sms
    is_marketing: bool
        to use different sms service
    """

    try:
        sms_sender = SmsSender()
        sms_sender.send_sms(phone_number, message, priority)
    except Exception as err:
        logger.exception('=== Failed to send SMS via celery task ===')


@app.task
def send_notification(devices, data):
    """
    Sends Push notification to the user devices

    Parameters
    ----------
    devices: list of app_platform.users.models.UserDevices
    data: dict
        contains push data
    device_type: str
        contains devices type
    """
    try:
        send_push_notification(devices, data)
    except Exception:
        logger.exception('Error while sending notification via celery')