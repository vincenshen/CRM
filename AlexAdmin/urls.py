"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from AlexAdmin import views


urlpatterns = [
    url(r'^$', views.AppIndex.as_view(), name="app_index"),
    # match all app_name and model_name, and transfer the app_name and model_name to ModelData View
    url(r'^(?P<app_name>\w+)/(?P<model_name>\w+)/$', views.ModelData.as_view(), name="model_data"),
    url(r'^(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<obj_id>\d+)/change/$', views.ObjChange.as_view(),
        name="obj_change"),
    url(r'^(?P<app_name>\w+)/(?P<model_name>\w+)/add/$', views.ObjCreate.as_view(),
        name="obj_add"),
    url(r'^(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<obj_id>\d+)/delete/$', views.ObjDelete.as_view(), name="obj_delete")
]
