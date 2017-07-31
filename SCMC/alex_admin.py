# -*- coding:utf-8 -*-
# @Time     : 2017-07-17 11:04
# @Author   : gck1d6o
# @Site     : 
# @File     : alex_admin.py
# @Software : PyCharm

from SCMC import models
from AlexAdmin.admin_base import site, BaseAdmin
from utils.export_csv import export_as_csv


class CustomerAdmin(BaseAdmin):
    list_display = ("id", "name", "qq", "consultant", "source", "status", "phone")
    list_filter = ("consultant", "source", "status", "name", "qq")
    search_fields = ("name", "qq", "source__name")
    list_per_page = 5
    filter_horizontal = ("tags", "consult_courses")
    actions = {"export_as_csv": export_as_csv}

site.register(models.Customer, CustomerAdmin)
site.register(models.Course)
site.register(models.ClassList)
