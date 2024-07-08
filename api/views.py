from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .serializers import UserSerializer
from django.http import HttpResponseRedirect
from django.urls import reverse
from api.models import CustomUser,CustomUserManager
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

@api_view(['GET', 'POST'])
@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        logout_message = request.COOKIES.get('logout_message')
        response = render(request, 'api/login.html', {'logout_message': logout_message})
        response.delete_cookie('logout_message')
        return response

    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'message': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'message': 'Invalid email or password.'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    response = HttpResponseRedirect(reverse('home'))
    response.set_cookie('auth_token', token.key)
    return response



@api_view(['GET', 'POST'])
@never_cache
def signup(request):
    if request.method == 'GET':
        return render(request, 'api/signup.html')

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return redirect('login')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'POST'])
@never_cache
def logout(request):
    auth_token = request.COOKIES.get('auth_token')
    if auth_token:
        try:
            token = Token.objects.get(key=auth_token)
            token.delete()
            response = redirect('login')
            response.set_cookie('logout_message', 'Successfully logged out.')
            response.delete_cookie('auth_token')
            return response
        except Token.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({'message': f'passed for {request.user.email}'})


@never_cache
def home(request):
    if 'auth_token' in request.COOKIES:
        return render(request, 'api/home.html', {'message': 'This is the home page'})
    else:
        return redirect('login')
