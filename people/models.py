from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
import hashlib
import random
import string
from django.conf import settings
SALT = getattr(settings, "EMAIL_TOKEN_SALT")
class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email :
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username')
        #判断邮件和用户名是否具有
        now = timezone.now()
        #获取当前django的时间
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            date_joined=now, 
            last_login=now,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, username, email, password):
        user = self.create_user(username,
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

#新版用户表
class Member(AbstractBaseUser):
    #AbstractBaseUser中只含有3个field: password, last_login和is_active.
    email = models.EmailField(verbose_name='邮箱',max_length=255,unique=True,)
    username = models.CharField(verbose_name="用户名", max_length=16, unique=True)
    weibo_id = models.CharField(verbose_name="新浪微博", max_length=30, blank=True)
    blog = models.CharField(verbose_name="个人网站", max_length=200, blank=True)
    location = models.CharField(verbose_name="城市", max_length=10, blank=True)
    profile = models.CharField(verbose_name="个人简介", max_length=140, blank=True)
    avatar = models.CharField(verbose_name="头像", max_length=128, blank=True)
    au = models.IntegerField(verbose_name="用户活跃度", default=0)
    last_ip = models.GenericIPAddressField(verbose_name="上次访问IP", default="0.0.0.0")
    email_verified = models.BooleanField(verbose_name="邮箱是否验证", default=False)
    date_joined = models.DateTimeField(verbose_name="用户注册时间", default=timezone.now)
    topic_num = models.IntegerField(verbose_name="帖子数", default=0)
    comment_num = models.IntegerField(verbose_name="评论数", default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()
    #objects就是我们之前一直使用的管理器
    #管理器用来维护我们的增删改查

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    #标签中的数据实例
    def is_email_verified(self):
        return self.email_verified
    #我们可以在模板中，通过实例出来的对象数据进行这个函数的调取，获取他是否验证过
    def get_weibo(self):
        return self.weibo_id

    def get_username(self):
        return self.username
        #方法的圆括号在templates标签中必需省略！！
    def get_email(self):
        return self.email
        #方法的圆括号在templates标签中必需省略！！

    def get_full_name(self):
        # The user is identified by their email address
        return self.email
        #get_full_name本来是获取first_name和last_name的
        #但是由于我们重新设置了表结构，那么这个函数必须自定义
        #方法的圆括号在templates标签中必需省略！！

    def get_short_name(self):
        # The user is identified by their email address
        return self.username
        #get_short_name获取first_name
        #但是由于我们重新设置了表结构，那么这个函数必须自定义
        #方法的圆括号在templates标签中必需省略！！

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    def calculate_au(self):
        """
        计算活跃度
        公式：Topic * 5 + Comment * 1
        """
        self.au = self.topic_num * 5 + self.comment_num * 1
        return self.au

    @property
    #类中函数可以直接做为属性使用
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
        
class Follower(models.Model):
    """
    用户的关系表
    B is the follower of A
    B 是 A 的关注者
    A 被 B 关注
    """
    user_a = models.ForeignKey(Member, related_name="user_a",verbose_name='偶像')
    user_b = models.ForeignKey(Member, related_name="user_b",verbose_name='粉丝')
    date_followed = models.DateTimeField(default=timezone.now,verbose_name='关注时间')

    class Meta:
        unique_together = ('user_a', 'user_b')

    def __str__(self):
        return "%s following %s" % (self.user_b, self.user_a)


class EmailVerified(models.Model):
    user = models.OneToOneField(Member, related_name="user")
    token = models.CharField("Email 验证 token", max_length=32, default=None)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s@%s" % (self.user, self.token)
    def generate_token(self):
        year = self.timestamp.year
        month = self.timestamp.month
        day = self.timestamp.day
        date = "%s-%s-%s" % (year, month, day)
        token = hashlib.md5((self.ran_str()+date).encode('utf-8')).hexdigest()
        return token
    def ran_str(self):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        return salt + SALT


class FindPass(models.Model):
    user = models.OneToOneField(Member, verbose_name="用户")
    token = models.CharField(max_length=32, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s@%s" % (self.user, self.token)
    def generate_token(self):
        year = self.timestamp.year
        month = self.timestamp.month
        day = self.timestamp.day
        date = "%s-%s-%s" % (year, month, day)
        token = hashlib.md5((self.ran_str()+date).encode('utf-8')).hexdigest()
        return token
    def ran_str(self):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        return salt + SALT
