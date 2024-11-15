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
    self.client = Client()
    self.json_request = {'content_type': 'application/json'}
    self.message = Message.objects.create(user_id = self.user.id, title = 'testtiltle', body = 'testbody' )
    self.bearer_token = 'Bearer '+jwt.encode({'email' : self.user.email}, 'zma', algorithm="HS256")

  def test_api_user_create(self):
    response = self.client.post(reverse('users'),json.dumps({"email": "test@test1.com"}),**self.json_request)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.json().get('email'), 'test@test1.com')

  def test_api_user_create_invalid_data_invalid_json(self):
    response = self.client.post(reverse('users'), json.dumps({"email": "test@test1.com"}) +'sd', **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'invalid json')

  def test_api_user_create_wrong_date(self):
    self.api_user_create_invalid_data_null_mail()
    self.api_user_create_invalid_data_exist_mail()
    self.api_user_create_invalid_data_exist_empty_srting()
    self.api_user_create_invalid_data_inccorect_mail()

  def api_user_create_invalid_data_null_mail(self):
    response = self.client.post(reverse('users'), json.dumps({"email": None}), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email cannot be empty')

  def api_user_create_invalid_data_exist_mail(self):
    response = self.client.post(reverse('users'), json.dumps({"email": 'test@test.com' }), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email alredy exist')

  def api_user_create_invalid_data_exist_empty_srting(self):
    response = self.client.post(reverse('users'), json.dumps({"email": '' }), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email cannot be empty')

  def api_user_create_invalid_data_inccorect_mail(self):
    response = self.client.post(reverse('users'), json.dumps({"email": 'test@test' }), **self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email is incorrect')

  def api_users_list(self):
    User.objects.create(email = 'test3@test3.com', json_web_token = create_jwt( 'test3@test3.com' ))
    User.objects.create(email = 'test2@test2.com', json_web_token = create_jwt( 'test2@test2.com' ))
    response = self.client.get(reverse('users'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('users')), 3)
    self.assertEqual(response.json().get('users')[2].get('email'), 'test2@test2.com')
    users_dic=[]
    for item in response.json().get('users'):
      users_dic.append(item.get('id'))
    self.assertEqual(users_dic, [1,2,3])

  def api_users_list_limit(self):
    User.objects.create(email = 'test3@test3.com', json_web_token = create_jwt( 'test3@test3.com' ))
    User.objects.create(email = 'test2@test2.com', json_web_token = create_jwt( 'test2@test2.com' ))
    response = self.client.get(reverse('users'), {'limit': 2 , 'offset': '0' })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('users')), 2)
    self.assertEqual(response.json().get('users')[1].get('email'), 'test2@test2.com')
    users_dic=[]
    for item in response.json().get('users'):
      users_dic.append(item)
    self.assertEqual(len(users_dic), 2)

  def test_api_users_list_limit_invalid_invalid_limit(self):
    User.objects.create(email = 'test3@test3.com', json_web_token = create_jwt( 'test3@test3.com' ))
    User.objects.create(email = 'test2@test2.com', json_web_token = create_jwt( 'test2@test2.com' ))
    response = self.client.get(reverse('users'), {'limit': 'sfsafa',  'offset': 'sdsd' })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('users')), 3)
    self.assertEqual(response.json().get('users')[2].get('email'), 'test2@test2.com')
    users_dic=[]
    for item in response.json().get('users'):
      users_dic.append(item.get('id'))
    self.assertEqual(users_dic, [1,2,3])


  def test_api_message_create(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"})
                                , **self.json_request, headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.json().get('title'), 'testtitle2')

  def test_api_message_create_wrong_date(self):
    self.api_message_create_invalid_data_invaldi_jwt()
    self.api_message_create_invalid_data_invaldi_not_exist_user()
    self.api_message_create_invalid_data_null_mail()
    self.api_message_create_invalid_data_empty_string_mail()
    self.api_message_create_invalid_json()
    self.api_message_create_invalid_empty_title()
    self.api_message_create_invalid_data_invaldi_without_jwt()

  def api_message_create_invalid_data_invaldi_jwt(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}), **self.json_request, headers = {'Authorization' :'invalidjwt'})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_create_invalid_data_invaldi_not_exist_user(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'bearer '+jwt.encode({'email' : 'notexsit@test.test'},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_create_invalid_data_invaldi_without_jwt(self):
    response = self.client.post(reverse('messages'),json.dumps({"title": "testtitle2", "body": "testbody2"}),**self.json_request)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_create_invalid_data_null_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'bearer '+jwt.encode({'email' : None},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_create_invalid_data_empty_string_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'bearer '+jwt.encode({'email' : ''},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_create_invalid_data_inccorect_mail(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"}),
                                  **self.json_request, headers = {'Authorization' :'bearer '+jwt.encode({'email' : 'asfasfasf'},
                                                                                                         'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'email is incorrect')

  def api_message_create_invalid_json(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "testtitle2", "body": "testbody2"})+'sfsf', **self.json_request, headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'invalid json')

  def api_message_create_invalid_empty_title(self):
    response = self.client.post(reverse('messages'),
                                json.dumps({"title": "", "body": "testbody2"}), **self.json_request, headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'title cannot be empty')

  def test_api_list_messages(self):
    Message.objects.create(user_id = self.user.id, title = 'testtiltle2', body = 'testbody2' )
    Message.objects.create(user_id = self.user.id, title = 'testtiltle3', body = 'testbody3' )
    response = self.client.get(reverse('messages'), headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('messages')), 3)
    self.assertEqual(response.json().get('messages')[2].get('body'), 'testbody3')
    message_dic=[]
    for item in response.json().get('messages'):
      message_dic.append(item.get('id'))
    self.assertEqual(message_dic, [1,2,3])

  def test_api_list_messages_query_params(self):
    Message.objects.create(user_id = self.user.id, title = 'testtiltle2', body = 'testbody2' )
    Message.objects.create(user_id = self.user.id, title = 'testtiltle3', body = 'testbody3' )
    response = self.client.get(reverse('messages'), {'search_by': 'body2'}, headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 200)
    print(response.json().get('messages'))
    self.assertEqual(response.json().get('messages')[0].get('body'), 'testbody2')
    message_dic=[]
    for item in response.json().get('messages'):
      message_dic.append(item.get('id'))
    self.assertEqual(message_dic, [2])

  def test_api_list_messages_query_params(self):
      Message.objects.create(user_id = self.user.id, title = 'testtiltle2', body = 'testbody2' )
      Message.objects.create(user_id = self.user.id, title = 'testtiltle3', body = 'testbody3' )
      response = self.client.get(reverse('messages'), {'limit': '1', 'offset': '0' }, headers = {'Authorization': self.bearer_token })
      self.assertEqual(response.status_code, 200)
      message_dic=[]
      for item in response.json().get('messages'):
        message_dic.append(item)
      self.assertEqual(len(message_dic), 1)

  def test_api_list_messages_wrong_query(self):
    Message.objects.create(user_id = self.user.id, title = 'testtiltle2', body = 'testbody2' )
    Message.objects.create(user_id = self.user.id, title = 'testtiltle3', body = 'testbody3' )
    response = self.client.get(reverse('messages'), {'limit': 'sdsd', 'offset': 'dsds' } ,headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('messages')), 3)
    self.assertEqual(response.json().get('messages')[2].get('body'), 'testbody3')
    message_dic=[]
    for item in response.json().get('messages'):
      message_dic.append(item.get('id'))
    self.assertEqual(message_dic, [1,2,3])

  def test_api_message_detail(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }), headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json().get('message')), 1)
    for item in response.json().get('message'):
      self.assertEqual(item.get('title'), 'testtiltle')

  def test_api_message_detail_wrong_date(self):
    self.api_message_detail_not_exist_pk()
    self.api_message_detail_invalid_data_invaldi_jwt()
    self.api_message_detail_invalid_data_not_exist_mail()
    self.api_message_detail_invalid_data_null_mail()
    self.api_message_detail_invalid_data_empty_string_mail()
    self.api_message_detail_invalid_data_inccorect_mail()

  def api_message_detail_without_jwt(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }))
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_detail_not_exist_pk(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': 1024}), headers = {'Authorization': self.bearer_token })
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'not any message to show')

  def api_message_detail_invalid_data_invaldi_jwt(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }), headers = {'Authorization': 'invalidjsfswt' })
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_detail_invalid_data_not_exist_mail(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }),
    headers = {'Authorization' :'bearer '+jwt.encode({'email' : 'notexsit@test.test'},'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_detail_invalid_data_null_mail(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }), headers = {'Authorization' :'bearer '+jwt.encode({'email' : None},
    'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_detail_invalid_data_empty_string_mail(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }), headers = {'Authorization' :'bearer '+jwt.encode({'email' : ''},
    'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')

  def api_message_detail_invalid_data_inccorect_mail(self):
    response = self.client.get(reverse('message',kwargs={ 'pk': self.message.id }), headers = {'Authorization' :'bearer '+jwt.encode({'email' : 'asfasfsaf'},
    'zma', algorithm="HS256")})
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()['error_message'], 'you are not authorised')
