from django.test import TestCase, Client
from django.urls import reverse
from api.models import User, Message
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
    self.json_request = {'content_type': 'application/json'}
    self.message = Message.objects.create(user_id = self.user.id, title = 'testtiltle', body = 'testbody' )
    self.Bearer_token = 'Bearer '+jwt.encode({'email' : self.user.email}, 'zma', algorithm="HS256")

  def test_api_create_view(self):
    response = self.client.post(reverse('users'),json.dumps({"email": "test@test1.com"}),**self.json_request)
    self.assertEqual(response.status_code, 201)

  def test_api_create_view_invalid_data__invalid_json(self):
    response = self.client.post(reverse('users'), json.dumps({"email": "test@test1.com"}) +'sd', **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'invalid json')

  def test_api_create_view_invalid_data_null_mail(self):
    response = self.client.post(reverse('users'), json.dumps({"email": None}), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email cannot be empty')

  def test_api_create_view_invalid_data_exist_mail(self):
    response = self.client.post(reverse('users'), json.dumps({"email": 'test@test.com' }), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email alredy exist')

  def test_api_create_view_invalid_data_exist_empty_srting(self):
    response = self.client.post(reverse('users'), json.dumps({"email": '' }), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email cannot be empty')

  def test_api_create_view_invalid_data_inccorect_mail(self):
    response = self.client.post(reverse('users'), json.dumps({"email": 'test@test' }), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email is incorrect')

  def test_api_list_view(self):
    response = self.client.get(reverse('users'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('users')), 3)

  def test_api_message_creation(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"})
                                , **self.json_request, headers = {'Authorization': self.Bearer_token })
    self.assertEqual(response.status_code, 201)

  def test_api_message_creation_invalid_data_invaldi_jwt(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}), **self.json_request, headers = {'Authorization' :'invalidjwt'})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'invalid jwt')

  def test_api_message_creation_invalid_data_not_exist_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'Bearer '+jwt.encode({'email' : 'notexsit@test.test'},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'user not exist')

  def test_api_message_creation_invalid_data_null_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'Bearer '+jwt.encode({'email' : None},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email cannot be empty')

  def test_api_message_creation_invalid_data_empty_string_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'Bearer '+jwt.encode({'email' : ''},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email cannot be empty')

  def test_api_message_creation_invalid_data_inccorect_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'Bearer '+jwt.encode({'email' : 'asfasfasf'},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email is incorrect')

  def test_api_message_creation_invalid_json(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"})+'sfsf', **self.json_request, headers = {'Authorization': self.Bearer_token })
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'invalid json')

  def test_api_message_creation_invalid_empty_title(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "", "body": "testbody2"}), **self.json_request, headers = {'Authorization': self.Bearer_token })
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'title cannot be empty')
