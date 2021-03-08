from django.urls import include, path, re_path
from rest_framework import routers
from .views import NotificationsViewSet, SendNotifications

router = routers.DefaultRouter()
router.register(r'notifications', NotificationsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    re_path(r'^send/$', SendNotifications.as_view()),
]