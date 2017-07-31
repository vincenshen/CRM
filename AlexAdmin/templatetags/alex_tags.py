# -*- coding:utf-8 -*-
# @Time     : 2017-07-17 17:49
# @Author   : gck1d6o
# @Site     : 
# @File     : alex_tags.py
# @Software : PyCharm

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_model_verbose_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def build_table_row(row, admin_class):
    """
    1. 循环admin_class.list_display, 通过反射取出每个字段的值
    2. 判断是否是第一个字段，如果是第一个字段，加上a标签
    3. 生成<tr></tr>元素返回给前端
    """

    # row_ele = "<tr>"
    row_ele = ""
    if admin_class.list_display:
        # 如果定义了list_display就获取row_obj中对应的字段
        for index, column_name in enumerate(admin_class.list_display):
            field_obj = row._meta.get_field(column_name)
            if field_obj.choices:
                column_display_func = getattr(row, "get_%s_display" % column_name)
                column_value = column_display_func()
            else:
                column_value = getattr(row, column_name)

            # index为0表示，第一个显示的字段
            if index == 0:
                td_ele = "<td><a href='{obj_id}/change/'>{column_value}</a></td>".format(obj_id=row.id, column_value=column_value)
            else:
                td_ele = "<td>{column_value}</td>".format(column_value=column_value)
            row_ele += td_ele
    else:
        # 如果没有定义list_display就获取row_obj的__str__方法
        column_value = row.__str__()
        td_ele = "<td><a href='#'>{column_value}</a></td>".format(column_value=column_value)
        row_ele += td_ele
    # row_ele += "</tr>"
    return mark_safe(row_ele)


@register.simple_tag
def build_filter_ele(filter_column, admin_class, filter_conditions):
    """
    filter_column: modelAdmin中定义的list_filter
    filter_conditions: 由list_filter作为key生成的字典

    1. 获取需要过滤字段的对象 field_obj.
    2. 调用field_obj.get_choices(): [('', '---------'), (1, 'QQ'), (2, 'Email')...].
    3. 生成select元素返回给前端.
    4. 循环choices列表，生成option元素.
    """
    field_obj = admin_class.model._meta.get_field(filter_column)
    # select_ele = "<select class='form-control' name=%s>" % filter_column
    select_ele = ""
    # filter_option = None 表示没有对这个字段过滤
    filter_option = filter_conditions.get(filter_column)
    try:
        for choice in field_obj.get_choices():
            select_ele += option_ele_func(filter_option=filter_option, choice=choice, choice_flag=True,
                                          selected_flag=True if filter_option else False)
    except AttributeError:
        # 非FK or Choice字段会报错，因此需要捕获并执行以下代码，通过field_name获取该列的所有值
        select_ele += "<option value="">---------</option>"
        for choice in admin_class.model.objects.values_list(filter_column).distinct():
            select_ele += option_ele_func(filter_option=filter_option, choice=choice,
                                          selected_flag=True if filter_option else False)
    # select_ele += "</select>"
    return mark_safe(select_ele)


def option_ele_func(filter_option=None, choice=None, choice_flag=False, selected_flag=False):
    """
    :param filter_option: 表示没有对这个字段过滤
    :param choice: model字段的值
    :param choice_flag: 是否有get_choices()方法
    :param selected_flag: 是否被选中
    """
    if selected_flag is True:
        if filter_option == str(choice[0]):
            selected = 'selected'
        else:
            selected = ""
        return "<option %s value=%s >%s</option>" % (selected, choice[0], choice[1] if choice_flag else choice[0])
    else:
        return "<option value=%s >%s</option>" % (choice[0], choice[1] if choice_flag else choice[0])


@register.simple_tag
def get_selected_m2m_objects(form_obj, field_name):
    """
    1. 根据field_name字段反射出form_obj.instance里面的字段对象
    2. 拿到字段对象，取出该字段所有数据
    """
    if getattr(form_obj.instance, form_obj.instance._meta.pk.name):
        field_obj = getattr(form_obj.instance, field_name)
        return field_obj.all()
    else:
        return []


@register.simple_tag
def get_unselected_m2m_objects(admin_class, field_name, selected_objects):
    """
    1. 根据field_name从admin_class.model反射出字段对象
    2. 拿到关联表的所有数据
    3. 返回数据
    """
    field_obj = getattr(admin_class.model, field_name)
    all_objects = field_obj.rel.to.objects.all()
    return set(all_objects) - set(selected_objects)


@register.simple_tag
def get_action(admin_class):
    action_dict = {}
    actions = admin_class.actions
    for k, v in actions.items():
        action_dict[k] = v.short_description
    return action_dict


@register.simple_tag
def get_field_verbose_name(admin_class, field_name):
    return admin_class.model._meta.get_field(field_name).verbose_name


@register.simple_tag
def object_delete(obj, model_name, recursive=False):
    """
    1. 通过obj.realted_objects拿到所有关联obj的关联对象关系列表
    2. 循环 关联对象关系表， 调用 i.get_accessor_name() 拿到反向查询的字段名
    3. 根据反向查询的字段名，拿到关联的对象 reverse_lookup_field
    4. 调用reverse_lookup_field.all(), 取得关联的query_set列表
    5. 对这个关联取得关联的query_set列表里每个对象再重复1,2,3步骤，直到没有更深入的关联关系为止

    :param obj:
    :param recursive:
    :return:
    """
    print('---obj', obj, obj._meta.related_objects)
    if not recursive:   # 首次调用
        ele = "<ul><li>{model_name}:{object_name}".format(model_name=model_name, object_name=obj)
    else:
        ele = "<ul>"

    local_m2m = obj._meta.local_many_to_many
    for m2m_field in local_m2m:
        m2m_objs = getattr(obj, m2m_field.name).all()
        for m2m_obj in m2m_objs:
            ele += "<li>{obj_name}:{m2m_name}</li>".format(obj_name=m2m_field.name, m2m_name=m2m_obj)

    for i in obj._meta.related_objects:    # step1
        reverse_lookup_key = i.get_accessor_name()    # step2
        try:
            reverse_lookup_field = getattr(obj, reverse_lookup_key)    # step3
            query_set = reverse_lookup_field.all()    # step4
            print('--->', reverse_lookup_key, query_set)
            child_ele = ""
            for o in query_set:
                print('------>o', o)
                child_ele += "<li>{model_verbose_name}:<a>{obj_name}</a></li>".format(
                                                                        model_verbose_name=o._meta.verbose_name,
                                                                        obj_name=o)
                if o._meta.related_objects:     # 代表还有下一层
                    child_ele += object_delete(o, recursive=True)    # step5
            child_ele += ""

            ele += child_ele
        except Exception as e:
            print(e)

    ele += "</ul>"
    return mark_safe(ele)