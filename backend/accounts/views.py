from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from accounts.tokenauthentication import JWTAuthentication
from .serializers import LoginSerializer, UserSerializer


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def login(request):
    serilizer = LoginSerializer(data=request.data)
    if serilizer.is_valid():
        token = JWTAuthentication.generate_token(payload=serilizer.data)
        return Response({
            "message": "Login Successfull",
            'token': token,
            'user': serilizer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serilizer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    jwt_auth = JWTAuthentication()

    try:
        user_token_tuple = jwt_auth.authenticate(request=request)
        print(user_token_tuple)
        if user_token_tuple is not None:
            return Response(True, status=200)
        else:
            return Response(False, status=401)
    except Exception as e:
        return Response(False, status=401)
