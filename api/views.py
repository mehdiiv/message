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

@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):

  def post(self, request):
    try:
      load_data = json.loads(request.body)
      data = {
      'email': load_data['email'],
      'json_web_token' : jwt.encode({'email' :load_data['email']},'zma' , algorithm="HS256")
      }
      error, error_message = self.valid(data)
      if error:
        return JsonResponse({'error': error_message}, status = 422)
      user = User.objects.create(**data)
      response = model_to_dict(user)
      return JsonResponse(response, status = 201)
    except json.JSONDecodeError :
      return JsonResponse({'error': 'token is in valid'}, status = 422)

  def valid(self , user):
    error = False
    error_message = []
    if user['email'] == '' :
      error = True
      error_message.append('email cannot be empty')
    if User.objects.filter(email = user['email']).exists():
      error = True
      error_message.append("email alredy exist")
    return error, error_message

  def get(self, request):
    users_dic = []
    users = User.objects.all()
    for item in users:
      response = model_to_dict(item)
    users_dic.append(response)
    return JsonResponse({'users': users_dic }, status = 200 )

@method_decorator(csrf_exempt, name='dispatch')
class MessageViews(View):
  def post(self, request):
    try:
      code = request.headers['Authorization']
      print('CODECODECODECODECODECODECODECODECODE',code)
      load_data = jwt.decode(code[7:], 'zma' , algorithms=["HS256"])
      print('load_dataload_dataload_dataload_dataload_dataload_data', load_data)
      user_id = User.objects.get(email = load_data['email']).id
      if  User.objects.filter(id = user_id).exists():
        return JsonResponse({'error': 'this user not exisit'}, status = 422)
      try:
        message_load_data = json.loads(request.body)
        data = {
        'title': message_load_data['title'],
        'body' : message_load_data['body']
        }
        message = Message.objects.create(user_id = user_id, **data)
        response = model_to_dict(message)
        return JsonResponse(response, status = 201)
      except json.JSONDecodeError :
        return JsonResponse({'error': 'invalid json'}, status = 422)
    except jwt.InvalidTokenError:
      return JsonResponse({'error': 'invalid jwt'}, status = 422)
