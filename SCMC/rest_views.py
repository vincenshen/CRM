# -*- coding:utf-8 -*-
# @Time     : 2017-07-12 17:23
# @Author   : gck1d6o
# @Site     : 
# @File     : rest_views.py
# @Software : PyCharm

from rest_framework import viewsets
from .models import MyUser
from .rest_searilizers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

