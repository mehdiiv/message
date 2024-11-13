from django.urls import path
from .views import UsersView, MessagesViews, MessageView

urlpatterns = [
  path('users/', UsersView.as_view(), name= 'users'),
  path('messages/', MessagesViews.as_view(), name= 'messages'),
  path('message/<int:pk>/', MessageView.as_view(), name= 'message'),
]
