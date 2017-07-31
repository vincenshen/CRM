from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Course, MyUser
from django.views import View
# Create your views here.
from .rest_searilizers import CourseSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from AlexAdmin.views import ModelData


@login_required
def index(request):
    if request.method == "GET":
        return render(request, "index.htm")


class Customer(View):
    app_name = "SCMC"
    model_name = "customer"
    model_data = ModelData()

    def get(self, request):
        """
        处理数据展示请求
        no_render选项让Model_data不直接渲染，而是返回所有局部变量
        """
        view_data_get = self.model_data.get(request, self.app_name, self.model_name, no_render=True)
        return render(request, "customer_list.html", view_data_get)

    def post(self, request):
        """处理导出CSV请求"""
        return self.model_data.post(request, self.app_name, self.model_name)


def user_login(request):
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user_obj = authenticate(username=username, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect(request.POST.get("next", "/index"))
        else:
            return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("/login")


@api_view(["GET", "POST"])
def courses_api(request):
    """Get all course list, or create a new course"""
    if request.method == "GET":
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        print(request)
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def course_detail(request, course_id):
    """Retrieve, update or delete a course"""
    course_obj = Course.objects.filter(id=course_id).first()
    if not course_obj:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        serializer = CourseSerializer(course_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = CourseSerializer(course_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        course_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
