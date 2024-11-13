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

def render_error(message, status = 422):
  return JsonResponse({'error_message': message}, status = status )

def fetch_data(json_data):
  try:
      return False, json.loads(json_data)
  except json.JSONDecodeError :
      return True, None

def valid_email(email):
  try:
    if email == '' or email == None:
      return True, 'email cannot be empty'
    validate_email(email)
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

@method_decorator(csrf_exempt, name='dispatch')
class UsersView(View):
  def post(self, request):
      error, load_data = fetch_data(request.body)
      if error:
        return render_error('invalid json')
      error, error_message = valid_email(load_data.get('email'))
      if error:
        return render_error(error_message)
      if User.objects.filter(email = load_data.get('email')).exists():
        return render_error('email alredy exist')

      user = User.objects.create(email = load_data['email'], json_web_token = jwt.encode({'email' :load_data['email']},'zma' , algorithm="HS256"))
      return JsonResponse(model_to_dict(user), status = 201)

  def get(self, _):
    users_list = []
    users = User.objects.all()
    for item in users:
      users_list.append(model_to_dict(item))
    return JsonResponse({'users': users_list }, status = 200)

@method_decorator(csrf_exempt, name='dispatch')
class MessagesViews(View):
  def post(self, request):
      error, load_data = authorization(request.headers['Authorization'])
      if error:
        return render_error('invalid jwt')

      error, error_message = valid_email(load_data.get('email'))
      if error:
        return render_error(error_message)
      object = User.objects.filter(email = load_data.get('email'))
      if not object.exists():
        return render_error('user not exist')
      user_id = object[0].id
      error , message_load_data = fetch_data(request.body)
      if error :
        return render_error('invalid json')
      if message_load_data['title'] == '' or message_load_data['title'] == None:
        return render_error('title cannot be empty')
#      elif Message.objects.filter(title = message_load_data['title']).exists:
#       return render_error('this title have been exist')
      message = Message.objects.create(user_id = user_id, title = message_load_data['title'], body = message_load_data['body'])
      return JsonResponse(model_to_dict(message), status = 201)

  def get(self, request):
    error, load_data =  authorization(request.headers['Authorization'])
    if error:
      return render_error('invalid jwt')
    error, error_message = valid_email(load_data.get('email'))
    if error:
      return render_error(error_message)
    object = User.objects.filter(email = load_data.get('email'))
    if not object.exists():
      return render_error('user not exist')
    message_list = []
    messges = Message.objects.all()
    for item in messges :
      message_list.append(model_to_dict(item))
    return JsonResponse({'messages' : message_list }, status = 200)

@method_decorator(csrf_exempt, name='dispatch')
class MessageView(View):
  def get(self, request, pk):
    error, load_data = authorization(request.headers['Authorization'])
    if error:
      return render_error('invalid jwt')
    error, error_message = valid_email(load_data.get('email'))
    if error :
      return render_error(error_message)
    object = User.objects.filter(email =load_data.get('email'))
    if not object.exists():
      return render_error('user not exist')
    message = Message.objects.filter(user_id = object[0].id, id = pk)
    if not message.exists():
      return render_error('not any message to show')
    message_list= []
    for item in message:
      message_list.append(model_to_dict(item))
    return JsonResponse({'message' : message_list}, status = 200)

  def post(self, request, pk):
    error, load_data = authorization(request.headers['Authorization'])
    if error:
      return render_error('invalid jwt')
    error, error_message = valid_email(load_data.get('email'))
    if error :
      return render_error(error_message)
    object = User.objects.filter(email =load_data.get('email'))
    if not object.exists():
      return render_error('user not exist')
    message = Message.objects.filter(user_id = object[0].id, id = pk)
    if not message.exists():
      return render_error('message not exist')
    error, message_load_data = fetch_data(request.body)
    if error:
      return render('invalid json')
    message_load_data = {
      'title': request.POST.get('title'),
      'body': request.POST.get('body')
    }
    message = message[0]
    for field, value in message_load_data.items():
        if value is not None:
          setattr(message, field, value)
    message.save()
    return JsonResponse({'message' : model_to_dict(message)}, status = 201)
