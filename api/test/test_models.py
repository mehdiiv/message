from django.test import TestCase
from api.models import User, Message
import jwt

class UserModelTest(TestCase):
  def setUp(self):
    self.jwt_code = jwt.encode({'email' : 'test@test.com'},'zma' , algorithm="HS256")
    self.user = User.objects.create(email = 'test@test.com', json_web_token = self.jwt_code)
    self.message = Message.objects.create(user_id = self.user.id , title = 'testtiltle', body = 'testbody')

  def test_user_ceration(self):
    self.assertEqual(self.user.email, 'test@test.com')
    self.assertEqual(self.user.json_web_token, self.jwt_code)

  def test_user_table_name(self):
    self.assertEqual(self.user._meta.db_table, 'users')

  def test_message_creation(self):
    self.assertEqual(self.message.title, 'testtiltle')
    self.assertEqual(self.message.body, 'testbody')

  def test_message_table_name(self):
    self.assertEqual(self.message._meta.db_table, 'messages')
