from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
# Create your models here.


class CustomerSource(models.Model):
    """客户来源"""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """备注"""
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    """课程详情"""
    name = models.CharField(max_length=32, unique=True)
    period = models.IntegerField(verbose_name="课程周期(月)")
    price = models.IntegerField(verbose_name="课程价格", help_text="课程价格")
    outline = models.TextField(verbose_name="课程大纲")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name


class Branch(models.Model):
    """校区"""
    name = models.CharField(max_length=64, unique=True)


class Contract(models.Model):
    """客户合同"""
    name = models.CharField(max_length=128, unique=True)
    content = models.TextField(verbose_name="合同内容")
    date = models.DateField(auto_now_add=True)


class ClassList(models.Model):
    """班级信息"""
    course = models.ForeignKey("Course")
    branch = models.ForeignKey("Branch")
    contract = models.ForeignKey("Contract")
    teachers = models.ManyToManyField("MyUser")
    semester = models.IntegerField(verbose_name="学期")
    class_type_choices = (
        (0, "周末班"),
        (1, "脱产班"),
        (2, "网络班")
    )
    class_type = models.IntegerField(choices=class_type_choices)
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(null=True, blank=True, verbose_name="毕业日期")

    class Meta:
        unique_together = ("course", "branch", "semester", "class_type")
        verbose_name = "班级信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s(%s)" % (self.course, self.semester)


class CourseRecord(models.Model):
    """上课记录"""
    class_name = models.ForeignKey("ClassList", verbose_name="班级")
    teacher = models.ForeignKey("MyUser")
    day_num = models.IntegerField(verbose_name="节次")
    name = models.CharField(max_length=128)
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, null=True, blank=True)
    homework_requirement = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("class_name", "day_num")

    def __str__(self):
        return "%s(%s)-%s" % (self.class_name, self.day_num, self.name)


class Customer(models.Model):
    """客户信息"""
    source = models.ForeignKey("CustomerSource", help_text="CustomerSource")
    consult_courses = models.ManyToManyField("Course", help_text="Course")
    referral_user = models.ForeignKey("MyUser", null=True, blank=True, related_name="referral_person")
    tags = models.ManyToManyField("Tag", blank=True)
    consultant = models.ForeignKey("MyUser", related_name="consultant_person")
    name = models.CharField(max_length=32, null=True, blank=True)
    qq = models.CharField(max_length=32, null=True, blank=True, unique=True, verbose_name="企鹅")
    wechat = models.CharField(max_length=64, null=True, blank=True, unique=True)
    phone = models.CharField(max_length=11, null=True, blank=True, unique=True)
    email = models.CharField(max_length=32, null=True, blank=True, unique=True)
    consultation_content = models.TextField(null=True, blank=True, verbose_name="咨询内容")
    status_choice = (
        (0, "已报名"),
        (1, "未报名"),
        (2, "已退费"),
    )
    status = models.SmallIntegerField(choices=status_choice, default=1)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "客户表"
        verbose_name_plural =  verbose_name


class PaymentRecord(models.Model):
    """缴费记录"""
    customer = models.ForeignKey("Customer")
    class_list = models.ForeignKey("ClassList")
    account = models.ForeignKey("MyUser")
    payment_method_choice = (
        (0, "现金"),
        (1, "微信"),
        (2, "支付宝"),
        (3, "刷卡"),
        (4, "贷款")
    )
    payment_method = models.SmallIntegerField(choices=payment_method_choice, verbose_name="付款方式")
    payment_type_choices = (
        (0, "报名费"),
        (1, "学费"),
        (2, "退费")
    )
    payment_type = models.SmallIntegerField(choices=payment_method_choice, verbose_name="付款类型")
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)


class CustomerFollowUp(models.Model):
    customer = models.ForeignKey("Customer")
    consultant = models.ForeignKey("MyUser")
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status_choices = (
        (0, "绝对不考虑"),
        (1, "短期不考虑"),
        (2, "近期会报名"),
        (3, "已试听"),
        (4, "已报名"),
        (5, "已在其他机构报名")
    )
    status = models.IntegerField(choices=status_choices)


class Enrollment(models.Model):
    """已报名课程"""
    account = models.ForeignKey("MyUser", verbose_name="用户")
    class_name = models.ForeignKey("ClassList", verbose_name="班级")
    date = models.DateTimeField(auto_now_add=True)


class StudyRecord(models.Model):
    """学习记录"""
    student = models.ForeignKey("MyUser", verbose_name="学生")
    course_record = models.ForeignKey("CourseRecord", verbose_name="上课记录")
    score_choices = (
        (100, "A+"),
        (90, "A"),
        (85, "B+"),
        (70, "B"),
        (65, "C+"),
        (60, "C"),
        (40, "C-"),
        (-50, "D"),
        (0, "N/A"),
        (-100, "COPY")
    )
    score = models.SmallIntegerField(choices=score_choices, verbose_name="成绩")
    attendance_status_choices = (
        (0, "签到"),
        (1, "迟到"),
        (2, "缺勤"),
        (3, "早退"),
        (4, "N/A")
    )
    attendance_status = models.SmallIntegerField(choices=attendance_status_choices, verbose_name="考勤")
    comment = models.TextField(null=True, blank=True, verbose_name="批注")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course_record")

    def __str__(self):
        return "%s%s" % (self.student, self.course_record)


class Menu(models.Model):
    """一级菜单"""
    name = models.CharField(max_length=128, unique=True)
    url_type_choices = (
        (0, "absolute"),
        (1, "relative")
    )
    url_type = models.PositiveIntegerField(choices=url_type_choices, default=1)
    url = models.CharField(max_length=128)
    order = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ("url", "url_type")

    def __str__(self):
        return self.name


class SubMenu(models.Model):
    """二级菜单"""
    menu = models.ForeignKey("Menu")
    name = models.CharField(max_length=128)
    url_type_choices = (
        (0, "absolute"),
        (1, "relative")
    )
    url_type = models.PositiveIntegerField(choices=url_type_choices, default=1)
    url = models.CharField(max_length=128)
    order = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ("url", "url_type")

    def __str__(self):
        return self.name


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=64, unique=True)
    menus = models.ManyToManyField("Menu", blank=True)

    def __str__(self):
        return self.name


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Create and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            username=username,
            email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(username=username, email=email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=32, unique=True, verbose_name="username")
    email = models.EmailField(max_length=128, unique=True, verbose_name="email address")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey("Role", null=True, blank=True)
    customer = models.OneToOneField("Customer", null=True, blank=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ["email"]

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_perms(self, perms, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        return self.is_admin
