from django.test import SimpleTestCase
from api.views import UserCreateView
from django.urls import reverse, resolve

class UrlTest(SimpleTestCase):
  def test_user_create_url(self):
    url = reverse('create_user')
    self.assertEqual(resolve(url).func.view_class, UserCreateView)
