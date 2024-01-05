from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout


from rest_framework import permissions
from rest_framework import views, status
from rest_framework.response import Response

from . import serializers


# Create your views here.
@login_required
def profile(request):
    return render(request, 'users/profile.html')


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)