from django.shortcuts import render, redirect
from django.views import View
from .pagenator import Paginator
from django.db.models import Q
# Create your views here.
from AlexAdmin import admin_modelform

from AlexAdmin import app_config  # 必须导入，获取每个APP下alex_admin.py里面site.register
from AlexAdmin.admin_base import site


class ModelData(View):
    """生成Model列表页面"""
    def get(self, request, app_name, model_name, no_render=False):
        """
        1. take model obj, get the model data,
        2. take model's admin class.
            the admin class include the model_obj, lister_display, list_filter, search_fields, list_per_page
        """
        if app_name in site.registered_admins:
            if model_name in site.registered_admins[app_name]:
                admin_class = site.registered_admins[app_name][model_name]
                queryset, paginator, filter_conditions, condition_str, search_str, order_key, new_order_key = self.get_filter_obj(request, admin_class)

        if no_render is True:
            return locals()
        return render(request, "alexadmin/obj_display.html", locals())

    def post(self, request, app_name, model_name, no_render=False):
        """
        process model admin actions
        """
        # get checked-box list
        checked_obj = request.POST.getlist("obj_id", "")
        # get action name str
        action_name = request.POST.get("_action")
        admin_class = self.model_class(app_name, model_name)
        if checked_obj:
            queryset = admin_class.model.objects.filter(id__in=checked_obj).only(*admin_class.list_display)
        else:
            queryset = admin_class.model.objects.only(*admin_class.list_display)
        response = admin_class.actions[action_name](admin_class, request, queryset)
        return response

    @staticmethod
    def model_class(app_name, model_name):
        if app_name in site.registered_admins:
            if model_name in site.registered_admins[app_name]:
                admin_class = site.registered_admins[app_name][model_name]
                return admin_class

    def get_filter_obj(self, request, admin_class):
        """
        1. take request, get url's parameter and request.path_info
        2. take admin_class, get search_fields, model_obj and list_per_page
        """
        queryset, search_str = self.search_condition(request, admin_class)    # 第一步进行search搜索
        queryset, filter_conditions = self.filter_condition(request, queryset)   # 第二步进行filter过滤
        queryset, order_key, new_order_key = self.order_by(request, queryset, admin_class)  # 第三步进行order_by排序

        # 对search信息, filter信息进行字符串拼接，用于过滤后的分页功能
        condition_str = "&search={search}".format(search=search_str)
        for k, v in filter_conditions.items():
            condition_str += "&%s=%s" % (k, v)

        queryset, paginator = self.page(request, queryset, admin_class, condition_str, order_key)  # 第四步分页功能
        return queryset, paginator, filter_conditions, condition_str, search_str, order_key, new_order_key

    @staticmethod
    def search_condition(request, admin_class):
        """关键字搜索"""
        search_str = request.GET.get("search", "")

        filter_conditions = {}
        for k, v in request.GET.items():
            if any([k == "_p", k == "search", k == "_o"]):
                continue
            if v:
                filter_conditions[k] = v
        if search_str:
            # 如果前端HTML页面有提交search搜索，就进行多字段Q查询拼接
            search_conditions = Q()
            search_conditions.connector = "OR"
            for search_field in admin_class.search_fields:
                search_conditions.children.append(("%s__icontains" % search_field, search_str))
            new_queryset = admin_class.model.objects.filter(search_conditions)
        else:
            new_queryset = admin_class.model.objects.all()
        return new_queryset, search_str

    @staticmethod
    def filter_condition(request, queryset):
        """字段过滤功能"""
        filter_conditions = {}
        for k, v in request.GET.items():
            if any([k == "_p", k == "search", k == "_o"]):
                continue
            if v:
                filter_conditions[k] = v
        new_queryset = queryset.filter(**filter_conditions)
        return new_queryset, filter_conditions

    @staticmethod
    def order_by(request, queryset, admin_class):
        """字段排序功能"""
        order_key = request.GET.get("_o", "")
        new_order_key = ""
        if order_key:
            new_queryset = queryset.order_by(order_key)
            if order_key.startswith("-"):
                new_order_key = order_key.strip("-")
            else:
                new_order_key = "-%s" % order_key
        else:
            new_queryset = queryset.order_by("-%s" % admin_class.model._meta.pk.name)
        return new_queryset, order_key, new_order_key

    @staticmethod
    def page(request, queryset, admin_class, condition_str, order_key):
        """
        分页功能
        :param request:
        :param queryset: 搜索、过滤和排序后的queryset
        :param admin_class:
        :param condition_str: 搜索、过滤和排序的字符串拼接
        :param order_key: 排序关键字
        :return:
        """
        all_count = queryset.count()

        # 排序关键字拼接，用于分页功能
        order_str = "&_o={order_key}".format(order_key=order_key)
        paginator = Paginator(request.GET.get("_p", ""), admin_class.list_per_page, all_count, request.path_info,
                              condition_str, order_str)
        new_queryset = queryset.only(*admin_class.list_display)[paginator.start: paginator.end]
        return new_queryset, paginator


class AppIndex(View):
    def get(self, request):
        return render(request, "alexadmin/app_index.html", {"site": site})


class ObjChange(View):
    """修改对象"""
    def get(self, request, app_name, model_name, obj_id):
        form, admin_class, instance_obj = self.model_form(app_name, model_name, obj_id)
        form_obj = form(instance=instance_obj)
        return render(request, "alexadmin/obj_change.html", locals())

    def post(self, request, app_name, model_name, obj_id):
        form, admin_class, instance_obj = self.model_form(app_name, model_name, obj_id)
        form_obj = form(instance=instance_obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
        return render(request, "alexadmin/obj_change.html", locals())

    @staticmethod
    def model_form(app_name, model_name, obj_id):
        if app_name in site.registered_admins:
            if model_name in site.registered_admins[app_name]:
                admin_class = site.registered_admins[app_name][model_name]
                form = admin_modelform.create_dynamic_modelform(admin_class.model)
                instance_obj = admin_class.model.objects.get(id=obj_id)
                return form, admin_class, instance_obj


class ObjCreate(View):
    """创建对象"""
    def get(self, request, app_name, model_name):
        form, admin_class = self.model_form(app_name, model_name)
        form_obj = form()
        return render(request, "alexadmin/obj_create.html", locals())

    def post(self, request, app_name, model_name):
        form, admin_class = self.model_form(app_name, model_name)
        form_obj = form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
        return render(request, "alexadmin/obj_create.html", locals())

    @staticmethod
    def model_form(app_name, model_name):
        if app_name in site.registered_admins:
            if model_name in site.registered_admins[app_name]:
                admin_class = site.registered_admins[app_name][model_name]
                form = admin_modelform.create_dynamic_modelform(admin_class.model)
                return form, admin_class


class ObjDelete(View):
    """删除对象视图"""
    def get(self, request, app_name, model_name, obj_id):
        admin_class = self.model_class(app_name, model_name)
        obj = admin_class.model.objects.get(id=obj_id)
        return render(request, "alexadmin/obj_delete.html", locals())

    def post(self, request, app_name, model_name, obj_id):
        admin_class = self.model_class(app_name, model_name)
        obj = admin_class.model.objects.get(id=obj_id)
        obj.delete()
        return redirect("/alex_admin/{app}/{model}/".format(app=app_name, model=model_name))

    @staticmethod
    def model_class(app_name, model_name):
        if app_name in site.registered_admins:
            if model_name in site.registered_admins[app_name]:
                admin_class = site.registered_admins[app_name][model_name]
                return admin_class
