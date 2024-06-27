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

@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'GET':
        return render(request, 'api/login.html')

    try:
        user = User.objects.get(username=request.data['username'])
    except User.DoesNotExist:
        return redirect('signup')

    if not user.check_password(request.data['password']):
        return Response({'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    response = HttpResponseRedirect(reverse('home'))
    response.set_cookie('auth_token', token.key)
    return response

@api_view(['GET', 'POST'])
def signup(request):
    if request.method == 'GET':
        return render(request, 'api/signup.html')

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        return redirect('login')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = Token.objects.get(key=request.auth.key)
        token.delete()
        response = redirect('login')  
        response.delete_cookie('auth_token')
        return response
    except Token.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({'message': f'passed for {request.user.email}'})

def home(request):
    if 'auth_token' in request.COOKIES:
        return render(request, 'api/home.html', {'message': 'This is the home page'})
    else:
        return redirect('login')
