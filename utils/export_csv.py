# -*- coding:utf-8 -*-
# @Time     : 2017-07-26 16:16
# @Author   : gck1d6o
# @Site     : 
# @File     : export_csv.py
# @Software : PyCharm

import datetime
import csv
import codecs
from django.http import HttpResponse


def export_as_csv(model_admin, request, queryset):
    """
    :param model_admin: 要求model_admin中必须定义list_display字段
    :param request:
    :param queryset: 为界面中选中的queryset obj集合
    :return: s
    """
    filename = queryset.model._meta.model_name + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    res = HttpResponse(content_type="text/csv")
    res["Content-Disposition"] = "attachment; filename={filename}.csv".format(filename=filename)
    res.write(codecs.BOM_UTF8)
    writer = csv.writer(res)
    writer.writerow(model_admin.list_display)

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in model_admin.list_display])
    return res

export_as_csv.short_description = "导出为CSV文件"
