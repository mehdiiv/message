from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import jwt
import json
from .models import User, Message

def find_user(code):
  try:
    load_data = jwt.decode(code[7:], 'zma', algorithms=['HS256'])
    return False, load_data['email']
  except jwt.InvalidTokenError :
    error_message = 'token is in valid'
    return True, error_message

def render_error(message, status = 422):
  return JsonResponse({'error_message': message}, status = status )

def fetch_data(json_data):
  try:
      return False, json.loads(json_data)
  except json.JSONDecodeError :
      return True, None

def valid(email):
  try:
    if email == '' or email == None:
      return True, 'email cannot be empty'
    validate_email(email)
    if User.objects.filter(email = email ).exists():
      return True, 'email alredy exist'
    return False,None
  except ValidationError:
    print(email)
    return True, 'email is incorrect'
def authorization(bearer_token):
  try:
      load_data = jwt.decode(bearer_token[7:], 'zma' , algorithms=["HS256"])
      return False, load_data
  except jwt.InvalidTokenError:
    return True, None

def valid_mail_messages(email):
  try:
    if email == '' or email == None:
      return True, 'email cannot be empty'
    validate_email(email)
    if not User.objects.filter(email = email ).exists():
      return True, 'user not exist'
    return False,None
  except ValidationError:
    print(email)
    return True, 'email is incorrect'

@method_decorator(csrf_exempt, name='dispatch')
class UsersView(View):

  def post(self, request):
      error, load_data = fetch_data(request.body)
      if error:
        return render_error('invalid data')
      error, error_message = valid(load_data.get('email'))
      if error:
        return render_error(error_message)

      user = User.objects.create(email = load_data['email'], json_web_token = jwt.encode({'email' :load_data['email']},'zma' , algorithm="HS256"))
      return JsonResponse(model_to_dict(user), status = 201)

  def get(self, request):
    users_dic = []
    users = User.objects.all()
    for item in users:
      users_dic.append(model_to_dict(item))
    return JsonResponse({'users': users_dic }, status = 200 )

@method_decorator(csrf_exempt, name='dispatch')
class MessagesViews(View):
  def post(self, request):
      error, load_data = authorization(request.headers['Authorization'])
      if error:
        return render_error('invalid jwt')
      error, error_message = valid_mail_messages(load_data.get('email'))
      if error:
        return render_error(error_message)
      user_id = User.objects.get(email = load_data['email']).id
      error , message_load_data = fetch_data(request.body)
      if error :
        return render_error('invalid json')
      message = Message.objects.create(user_id = user_id, title = message_load_data['title'], body = message_load_data['body'])
      return JsonResponse(model_to_dict(message), status = 201)
