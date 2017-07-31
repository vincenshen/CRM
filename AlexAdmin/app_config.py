# -*- coding:utf-8 -*-
# @Time     : 2017-07-17 10:59
# @Author   : gck1d6o
# @Site     : 
# @File     : app_config.py
# @Software : PyCharm
import inspect
from django.conf import settings

# 导入INSTALLED_APPS中注册的APP下alex_admin.py
for app_name in settings.INSTALLED_APPS:
    try:
        __import__("%s.%s" % (app_name, "alex_admin"))
    except ImportError:
        pass
