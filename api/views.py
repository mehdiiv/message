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

from .models import User
@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(View):


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
