# -*- coding:utf-8 -*-
# @Time     : 2017-07-12 17:23
# @Author   : gck1d6o
# @Site     : 
# @File     : rest_urls.py
# @Software : PyCharm


from django.conf.urls import url, include
from rest_framework import routers
from .rest_views import UserViewSet
from .views import courses_api, course_detail

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include("rest_framework.urls", namespace="rest_framework")),
    url(r'^courses/$', courses_api),
    url(r'^courses/(\d+)$', course_detail)
]