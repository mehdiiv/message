from django.urls import path
from .views import UserView, MessageViews

urlpatterns = [
  path('user/', UserView.as_view(), name= 'user'),
  path('message/', MessageViews.as_view(), name= 'message'),
]
