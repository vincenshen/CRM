# -*- coding:utf-8 -*-
# @Time     : 2017-07-12 17:54
# @Author   : gck1d6o
# @Site     : 
# @File     : rest_searilizers.py
# @Software : PyCharm

from rest_framework import serializers
from .models import MyUser, Course


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ("url", "username", "email", "is_active", "is_staff")


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "period", "price", "outline")
