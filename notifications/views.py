import json
import logging

from celery.decorators import task
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .serializers import NotificationSerializer
from .models import Notifications
from .tasks import send_sms,send_push_notification
from users.models import User, UserDevices
logger = logging.getLogger(__name__)

class NotificationsViewSet(viewsets.ModelViewSet):
    queryset = Notifications.objects.all().order_by('date_sent')
    serializer_class = NotificationSerializer



class SendNotifications(APIView):
    serializer_class = NotificationSerializer
    task(name="send_notification_task")
    def post(self, request, format=None):
        """
        Sends sms view function
        """
        try:
            notification_serializer = self.serializer_class(data=request.data)
            if notification_serializer.is_valid():
                response_data = {"message":""}
                response_data["message"] = "Success in sending notification"
                response_status_code = status.HTTP_200_OK
                notification_type = notification_serializer.data.get('type')
                notification_subject = notification_serializer.data.get('subject')
                notification_body = notification_serializer.data.get('body')
                notification_category = notification_serializer.data.get('category')
                language = notification_serializer.data.get('notificationLanguage')
                notification_sender = notification_serializer.data.get('sender')
                user_sender = User.objects.get(id = notification_sender)
                sender_mobile_no = str(user_sender.mobile_number)
                notification_priority = request.data['priority']
                #sending sms notification to users
                #sending group notifications
                if request.data['notificationType'] == 'Text':
                    if request.data['category'] == 'Group':
                        users_list = request.data['recipient_list']
                        users_obj = User.objects.filter(id__in=users_list)
                        users_mobile_numbers = []
                        for user in users_obj:
                            Notifications.objects.create(subject=notification_subject, body=notification_body, 
                            notification_language=language, category=notification_category, notification_type=notification_type,
                                sender=user_sender, recipient=user)
                            users_mobile_numbers.append(str(user.mobile_number))
                        for mobile_no in users_mobile_numbers:
                            #celery task for sending message
                            send_sms.delay(sender_mobile_no, mobile_no, notification_body, notification_priority)

                    #sending individual notifications    
                    else:
                        notification_receiver = notification_serializer.data.get('recipient')
                        user_receiver = User.objects.get(id = notification_receiver)
                        receiver_mobile_no = str(user_receiver.mobile_number)
                        Notifications.objects.create(subject=notification_subject, body=notification_body, 
                        notification_language=language, category=notification_category, notification_type=notification_type,
                        sender=user_sender, recipient=user_receiver)
                        #celery task for sending message
                        send_sms.delay(sender_mobile_no, receiver_mobile_no, notification_body, notification_priority)
                else:
                    #sending push notifications notification type is Push
                    notification_subject = notification_serializer.data.get('subject')
                    notification_body = notification_serializer.data.get('body')
                    notification_receiver = notification_serializer.data.get('recipient')
                    user_receiver = User.objects.get(id = notification_receiver)
                    user_push_ids = UserDevices.objects.filter(user = user_receiver).values('push_id')
                    Notifications.objects.create(subject=notification_subject, body=notification_body, 
                        notification_language=language, category=notification_category, notification_type=notification_type,
                            sender=user_sender, recipient=user_receiver)
                    push_ids = [push['push_id'] for push in user_push_ids]
                    data={'heading':subject, 'alert': body},
                    send_push_notification.delay(push_ids, data)
                return Response(response_data, response_status_code)
            else:
                response_data["message"] = str(notification_serializer.errors)
                response_status_code = status.HTTP_400_BAD_REQUEST
                logger.exception('serializers errors are: ',notification_serializer.errors)
                return Response(response_data, response_status_code)
        except Exception as err:
            response_data = {"message":""}
            logger.exception("Something went wrong! {msg}?".format(msg=str(err)))
            response_data["message"] = str(err)
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        

