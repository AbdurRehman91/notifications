import http.client
import logging
from datetime import datetime, timedelta
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

class ApiResponseStatuses:
    """
    Types of API response status
    """

    OK = 'OK'
    ERROR = 'Error'
    TIMEOUT_ERROR = 'Timeout'

def send_push_notification(installation_ids, data):
    """
    Send push notification to devices.

    Parameters
    ----------
    installation_ids: list
        List of device push_ids
    data: dict
        Data for sending push notification
    Returns
    -------
    dict
        API response
    """
    try:
        http_connection = http.client.HTTPSConnection('onesignal.com', 443)
        http_connection.connect()
        push_data = {
            'app_id': settings.ONESIGNALAPP_ID,
            'include_player_ids': installation_ids,
            'content_available': True,
            'data': data
        }
        
        push_data.update({'contents': {'en': data.get('alert', '')}})
        push_data.update({'headings': {'en': data.get('headings', '')}})
        
        # SAMPLE POST api call for sending push notification
        http_connection.request('POST', '/api/', json.dumps(push_data), {'Content-Type': 'application/json'})
        response = http_connection.getresponse()
        if response.status == 200:
            logger.info('push notification response is : {}'.format(response))
            return {'result': response.read().decode("utf-8")}
        else:
            logger.exception('Error sending push status {}'.format(response.status))
            return {'result': False}
    except BaseException as ex:
        logger.exception('Error sending push : {}'.format(str(ex)))
        return {'result': False}

class TwilioSmsService:
    """
    Service to send sms using twilio
    """

    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.sms_from = settings.TWILIO_SMS_FROM

    def send_sms(self, receiver, message):
        """
        Sends SMS using twilio sms service.
        Parameters
        ----------
        receiver: object
            phone_number of user
        message: str
            text message which will be sent

        Returns
        -------
        tuple
            response status and message
        """

        receiver = str(receiver).replace(' ', '')  # remove empty spaces in phone number
        message = self.client.messages.create(body=message, from_=self.sms_from, to=receiver)
        logger.info('Sent resend OTP to {} using Twilio'.format(receiver))
        if message.error_code:
            return ApiResponseStatuses.ERROR, message.error_message
        return ApiResponseStatuses.OK, 'Success'

class DefaultSmsService:
    """
    Service for sending sms through default(Telecom) sms api
    """

    ERROR_CODES = {
        'Error 200': 'Failed login. Username and password do not match.',
        'Error 201': 'Unknown MSISDN, Please Check Format i.e. 92345xxxxxxx',
        'Error 203': 'SMS operation not allowed',
        'Error 100': 'Out of credit',
        'Error 102': 'Invalid session ID or the session has expired. Login again',
        'Error 103': 'Invalid Mask',
        'Error 104': 'Invalid Operator Id'
    }

    def send_sms(self, sender, receiver, message):
        """
        Sends sms to the given number
        Parameters
        ----------
        receiver: str
            mobile number
        sender: str
            mobile number
        message: str
            message string
        
        """

class SmsSender:
    """Main utility used for send sms using multiple API's"""

    default_sms_service = DefaultSmsService()
    high_priority_sms_service = TwilioSmsService()

    def __init__(self, sms_service=None):
        if sms_service:
            self.sms_service = sms_service

    def send_sms(self, sender, receiver, message, priority=None):
        """
        Sends sms based on the provided params, e.g. multiple services for different typ of messages.
        Parameters
        ----------
        sender: str
            phone number of the sender
        receiver: str
            phone number of the receiver
        message: str
            text for sms
        priority: bool
            is priority sms
        Returns
        -------
        tuple or status code
            (status, message) or status code
        """

        if priority:
            return self.high_priority_sms_service.send_sms(receiver, message)

        else:
            res, _ = self.default_sms_service.send_sms(sender, receiver, message)

        if res in [ApiResponseStatuses.TIMEOUT_ERROR, ApiResponseStatuses.ERROR]:
            logger.info('Retyring sms sending using default sms service')
            return self.default_sms_service.send_sms(sender, receiver, message)
        return res

def year_ahead():
    return datetime.today() + timedelta(days=360)