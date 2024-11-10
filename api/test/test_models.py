from django.test import TestCase
from api.models import User
import jwt

class UserModelTest(TestCase):
  def setUp(self):
    self.jwt_code = jwt.encode({'email' : 'test@test.com'},'zma' , algorithm="HS256")
    self.user = User.objects.create(email = 'test@test.com', json_web_token = self.jwt_code)

  def test_user_ceration(self):
    self.assertEqual(self.user.email, 'test@test.com')
    self.assertEqual(self.user.json_web_token, self.jwt_code)

  def test_user_table_name(self):
    self.assertEqual(self.user._meta.db_table, 'users')
