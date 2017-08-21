from django.http import HttpResponse, HttpResponseRedirect
from people.forms import ProfileForm, PasswordChangeForm
from people.models import Member
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
import base64
import json
from django.conf import settings

from qiniu import Auth
import qiniu.config
from qiniu import BucketManager
AK = 'C5tO1JIwAN1xmcWFl5NmNYGxgmpQMaycmECTz9Yk'
SK = 'R4VpaCon0_V4pJPWZoXmD4P7XPMX85mAtwj2b9UI'


SITE_URL = getattr(settings, "SITE_URL")
#SITE_URL = 'ouiwyzbcj.bkt.clouddn.com'
@csrf_protect
@login_required
def profile(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        #instance 实例当前对象
        #表单接收instance一个实例，之后的save将更新这个对象而不是创建
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, "设置已更新")
            return render(request, "people/settings.html", {"form": form})
    else:
        form = ProfileForm(instance=user)

#https://portal.qiniu.com/bucket/avatar/resource
    q = Auth(AK, SK)
    bucket_name = 'avatar'
    key_name = 'avatar/' + user.username
    

    returnBody = '{"name": $(fname), "key": $(key)}'
    returnUrl = SITE_URL + reverse("user:upload_headimage")
    mimeLimit = "image/jpeg;image/png"

    policy = {'returnUrl':returnUrl,'returnBody':returnBody,'mimeLimit':mimeLimit}

    uptoken = q.upload_token(bucket_name,key_name,3600,policy)
    # {'returnUrl':'http://127.0.0.1:8000/photos/uploadprocessor', 
    # 'returnBody': '{"name": $(fname), "key": $(key)}', 
    # 'mimeLimit':'image/jpeg;image/png'
    # } 
    # 其中upload_token函数用于生成表单里的token字段，
    # upload_token函数中的7200代表上传凭证的有效期，
    # returnUrl表示上传成功后的重定向地址，
    # returnBody表示重定向时七牛返回的信息，它是一个base64编码后的json数据，需要解码获取json数据
    # 当上传出错时错误信息直接在url中以明文的形式出现，并不会在返回的json数据里
    # 通过设置mimeLimit还可以限制上传文件的类型。
    # fsizeLimit 大小尺寸
    return render(request, "people/settings.html", {
        "form": form,
        "user": user,
        "uptoken":uptoken
        })

@csrf_protect
@login_required
def password(request):
    user = request.user

    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            data = form.clean()
            if user.check_password(data["old_password"]):
                user.set_password(data["password"])
                user.save()
                messages.success(request, "新密码设置成功！请重新登录")
                auth_logout(request)
                return HttpResponseRedirect(reverse("user:login"))
            else:
                messages.error(request,'当前密码输入错误')
                return render(request, "people/password.html", {"form": form})
    else:
        form = PasswordChangeForm()

    return render(request, "people/password.html", {
        "form": form,
        })

# 头像上传
@csrf_protect
@login_required
def upload_headimage(request):
    user = request.user
    if request.method == "GET":
        print(request.GET)
        #<QueryDict: {'upload_ret': ['eyJuYW1lIjogIjIuanBnIiwgImtleSI6ICJhdmF0YXIvcm9vdCJ9']}>
        try:
            retstr = request.GET.get('upload_ret')
            #这个ReturnUrl的链接后会跟着一个?upload_ret=XXX，
            #可以用get方法获取这个upload_ret
            #upload_ret的内容是base64安全编码的json形式的key值
            retstr = retstr.encode("utf-8")
            dec = base64.urlsafe_b64decode(retstr)
            ret = json.loads(dec)
            if ret and ret['key']:
            #upload_ret对应上传之后返回的信息
            #其中的key值对应图片名字
                request.user.avatar = ret['key']
                request.user.save()
            else:
                raise
            messages.success(request, '头像上传成功！')
        except:
            messages.error(request, '头像上传失败！')

    return HttpResponseRedirect(reverse("user:settings"))

# 头像删除
@csrf_protect
@login_required
def delete_headimage(request):
    user = request.user

    if user.avatar == None or user.avatar == '':
        messages.error(request, '亲，你还没上传头像呢！')
    else:
        q = Auth(AK, SK)
        bucket = BucketManager(q)
        bucket_name = 'avatar'
        ret, info = bucket.delete(bucket_name, user.avatar)
        if ret is None:
            messages.error(request, '头像删除失败')
        else:
            user.avatar = ''
            user.save()
            messages.success(request, '头像删除成功')

    return HttpResponseRedirect(reverse("user:settings"))