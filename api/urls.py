from django.urls import path
from .views import UsersView, MessagesViews

urlpatterns = [
  path('users/', UsersView.as_view(), name= 'users'),
  path('messages/', MessagesViews.as_view(), name= 'messages'),
]
