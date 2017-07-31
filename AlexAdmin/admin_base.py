# -*- coding:utf-8 -*-
# @Time     : 2017-07-17 11:06
# @Author   : gck1d6o
# @Site     : 
# @File     : admin_base.py
# @Software : PyCharm


class BaseAdmin(object):
    list_display = ()
    list_filter = ()
    list_per_page = 5


class AdminSite(object):
    def __init__(self):
        self.registered_admins = {}

    def register(self, model, admin_class=None):
        """
        Registers the given model(s) with the given admin class.
        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use BaseAdmin (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.

        If a model is already registered, this will raise AlreadyRegistered.
        If a model is abstract, this will raise ImproperlyConfigured.
        """
        if not admin_class:
            admin_class = BaseAdmin()

        # 将model装载到admin_class中，以供后面simple_tags调用，因为直接传递model的到HTML前端会报错。
        admin_class.model = model

        # 通过model._meta获取model所在的APP的名称
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        self.registered_admins.setdefault(app_label, {}).update({model_name: admin_class})


"""实例化AdminSite以便APP下自定义Admin调用"""
site = AdminSite()
