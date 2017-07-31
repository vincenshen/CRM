# -*- coding:utf-8 -*-
# @Time     : 2017-07-24 16:17
# @Author   : gck1d6o
# @Site     : 
# @File     : admin_modelform.py
# @Software : PyCharm
from django.forms import ModelForm


def __new__(cls, *args, **kwargs):
    """实现HTML表单bootstrap样式为form-control"""
    for field_name in cls.base_fields:
        field = cls.base_fields[field_name]
        attr_dic = {"class": "form-control"}
        field.widget.attrs.update(attr_dic)
    return ModelForm.__new__(cls)


def create_dynamic_modelform(model_class):
    """
    通过type动态创建ModelForm
    """
    class Meta:
        model = model_class
        fields = "__all__"

    dynamic_modelform = type("DynamicModelForm", (ModelForm, ), {"Meta": Meta, "__new__": __new__})
    return dynamic_modelform
