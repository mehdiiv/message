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
from django.db.models import Q

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
  if bearer_token == None:
    return True, None
  try:
      load_data = jwt.decode(bearer_token[7:], 'zma' , algorithms=["HS256"])
      error, _ = valid_email(load_data.get('email'))
      if error:
        return True, None
      objects = User.objects.filter(email = load_data.get('email'))
      if not objects.exists():
        return True, None
      return False, objects[0]
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

  def get(self, request):
    users_list = []
    users = User.objects.all()
    if request.GET.get('limit') != None and request.GET.get('limit').isdigit():
      limit = int(request.GET.get('limit'))
      users = users[:limit]

    for item in users:
      users_list.append(model_to_dict(item))
    return JsonResponse({'users': users_list }, status = 200)

@method_decorator(csrf_exempt, name='dispatch')
class MessagesViews(View):
  def post(self, request):
      error, user = authorization(request.headers.get('Authorization'))
      if error :
        return render_error('you are not authorised')

      error , message_load_data = fetch_data(request.body)
      if error :
        return render_error('invalid json')
      if message_load_data['title'] == '' or message_load_data['title'] == None:
        return render_error('title cannot be empty')
      elif Message.objects.filter(title = message_load_data['title'], user = user).exists():
       return render_error('this title have been exist')
      message = Message.objects.create(user = user, title = message_load_data['title'], body = message_load_data['body'])
      return JsonResponse(model_to_dict(message), status = 201)

  def get(self, request):
    error, user = authorization(request.headers.get('Authorization'))
    if error :
      return render_error('you are not authorised')
    messges = Message.objects.filter(user = user)
    if request.GET.get('search_by') != None :
       search_by = request.GET.get('search_by')
       messges = Message.objects.filter(Q(body__icontains= search_by ),user = user)
    if request.GET.get('limit') != None and request.GET.get('limit').isdigit():
      print('244444444',type(request.GET.get('limit')))
      limit = int(request.GET.get('limit'))
      messges = messges[:limit]

    messages_list = []
    for item in messges :
      messages_list.append(model_to_dict(item))
    return JsonResponse({'messages' : messages_list }, status = 200)

@method_decorator(csrf_exempt, name='dispatch')
class MessageView(View):
  def get(self, request, pk):
    error, user = authorization(request.headers.get('Authorization'))
    if error :
      return render_error('you are not authorised')
    message = Message.objects.filter(user = user, id = pk)
    if not message.exists():
      return render_error('not any message to show')
    message_list= []
    for item in message:
      message_list.append(model_to_dict(item))
    return JsonResponse({'message' : message_list}, status = 200)

  def post(self, request, pk):
    error, user = authorization(request.headers.get('Authorization'))
    if error :
      return render_error('you are not authorised')
    message = Message.objects.filter(user = user, id = pk)
    if not message.exists():
      return render_error('message does not exist')
    error, message_load_data = fetch_data(request.body)
    if error:
      return render('invalid json')
    data = {
      'title': message_load_data.get('title'),
      'body': message_load_data.get('body')
    }
    message = message[0]
    for field, value in data.items():
        if value is not None:
          setattr(message, field, value)
    message.save()
    return JsonResponse({'message' : model_to_dict(message)}, status = 201)
