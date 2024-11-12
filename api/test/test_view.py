from django.test import TestCase, Client
from django.urls import reverse
from api.models import User
from django.http import JsonResponse
import jwt
import json

def create_jwt(email):
  return jwt.encode({'email' : email },'zma' , algorithm="HS256")

class ApiTest(TestCase):
  def setUp(self):
    create_jwt( email = 'test@test.com' )
    self.user = User.objects.create(email = 'test@test.com', json_web_token = create_jwt( 'test@test.com' ))
    self.user2 = User.objects.create(email = 'test3@test3.com', json_web_token = create_jwt( 'test3@test3.com' ))
    self.user3 = User.objects.create(email = 'test2@test2.com', json_web_token = create_jwt( 'test2@test2.com' ))
    self.client = Client()

  def test_api_create_view(self):
    json_request = {'content_type': 'application/json'}
    response = self.client.post(reverse('users'),json.dumps({"email": "test@test1.com"}),**json_request)
    self.assertEqual(response.status_code, 201)

  def test_api_list_view(self):
    response = self.client.get(reverse('users'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('users')), 3)
