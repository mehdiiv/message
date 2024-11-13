from django.test import SimpleTestCase
from api.views import UsersView, MessagesViews
from django.urls import reverse, resolve

class UrlTest(SimpleTestCase):
  def test_user_create_url(self):
    url = reverse('users')
    self.assertEqual(resolve(url).func.view_class, UsersView)

  def test_message_create(self):
    url = reverse('messages')
    self.assertEqual(resolve(url).func.view_class, MessagesViews )
