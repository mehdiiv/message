from django.test import TestCase, Client
from django.urls import reverse
from api.models import User
from django.http import JsonResponse
import jwt
import json

class ApiTest(TestCase):
  def setUp(self):
    self.jwt_code = jwt.encode({'email' : 'test@test.com'},'zma' , algorithm="HS256")
    self.user = User.objects.create(email = 'test@test.com', json_web_token = self.jwt_code)
    self.client = Client()

  """ def test_api_create_view(self):
    json_email_data = json.dumps({"email": "test@test1.com"})
    print('^^^^^^^^^^^^^^^', type(json_email_data))
    print('$###################', type(json_email_data))
    response = self.client.post(reverse('create_user'),json_email_data)
    print( '%%%%%%%%%%%%%%',response.json())
    self.assertEqual(response.status_code, 201) """

  def test_api_list_view(self):
    response = self.client.get(reverse('create_user'))
    self.assertEqual(response.status_code, 200)
