from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from people.forms import RegisterForm, LoginForm
from people.models import Member, Follower, EmailVerified as Email, FindPass
from question.models import Topic, Comment
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login
from django.utils import timezone
from django.core.cache import cache
from pro.settings import NUM_TOPICS_PER_PAGE,NUM_COMMENT_PER_PAGE
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
import datetime


SITE_URL = getattr(settings, "SITE_URL", "http://localhost:8080")


@csrf_protect
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            #data = form.clean()
            #字段的验证方法在调用 clean() 时会运行
            data = form.cleaned_data
            new_user = Member.objects.create_user(username=data["username"],
                                                  email=data["email"],
                                                  password=data["password"])
            # Email 验证
            new_user.save()

            email_verified = Email(user=new_user)
            email_verified.token = email_verified.generate_token()
            email_verified.save()

            send_mail(u"欢迎加入", u"%s 你好：\r\n 请点击链接验证您的邮箱 %s%s" % (new_user.username,SITE_URL, reverse("user:email_verified", args=(new_user.id, email_verified.token))),
                       "18636030403@163.com", [data["email"]]
                    )
            messages.success(request, u"恭喜您注册成功，请去您的邮箱验证一下您的邮箱，如果未收到邮件，请去垃圾信箱看一下。")

            #注册成功后自动登陆
            user = authenticate(email=data["email"], password=data["password"])
            auth_login(request, user)
            go = reverse("question:index")
            #reverse使用name定义的命名空间

            # if request.session.get("next"):
            #     go = request.session.pop("next")
            # #session的工作过程
            # #生成随机字符串
            # #写到用户浏览器的cookie中
            # #保存到session中
            # #在随机字符串对应的字典中设置相关内容    

            is_auto_login = request.POST.get('auto')
            if not is_auto_login:
                request.session.set_expiry(0)
            #     #request.session.set_expiry设置session的有效期
            #     #如果value是个整数，session会在些秒数后失效。
            #     #如果value是个datatime或timedelta，session就会在这个时间后失效。
            #     #如果value是0,用户关闭浏览器session就会失效。
            #     #如果value是None,session会依赖全局session失效策略。
            return HttpResponseRedirect(go)
            #HttpResponseRedirect将客户端重定向到新的 URL。
    else:
        form = RegisterForm()
    return render(request, 'people/register.html', {
        'form': form,
        })


@csrf_protect
def login(request):
    if request.user.is_authenticated():
    	#is_authenticated：用来判断用户是否登陆
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
        #HTTP Referer是header的一部分，当浏览器向web服务器发送请求的时候，一般会带上Referer
        #告诉服务器我是从哪个页面链接过来的，服务器基此可以获得一些信息用于处理。
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # 邮箱
            username = data["username"]
            if '@' in username:
                email = username
            else:
                user = Member.objects.get(username=username)
                email = user.email
            user = authenticate(email=email, password=data["password"])
            #密码有效返回User对象
            #密码无效返回None
            if user is not None:
                auth_login(request, user)
                go = reverse("question:index")
                 
                # if request.session.get("next"):
                #     go = request.session.pop("next")

                is_auto_login = request.POST.get('auto')
                if not is_auto_login:
                    request.session.set_expiry(0)
                return HttpResponseRedirect(go)
            else:
                messages.error(request, '密码不正确！')
                return render(request,'people/login.html',locals())
    else:
        form = LoginForm()

    # if request.GET.get("next"):
    #     request.session["next"] = request.GET["next"]

    return render(request, 'people/login.html', {
        'form': form
        })

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('question:index'))

#用户信息
def user(request, uid):
    user_from_id = Member.objects.get(pk=uid)
    user_a = request.user
    if user_a.is_authenticated():
        try:
            follower = Follower.objects.filter(user_a=user_a, user_b=user_from_id).first()
        except (Member.DoesNotExist, Follower.DoesNotExist):
            follower = None

    topic_list = Topic.objects.order_by("-created_on").filter(author=user_from_id.id)[:10]
    comment_list = Comment.objects.order_by("-created_on").filter(author=user_from_id)[:10]
    return render(request, "people/user.html", locals())

#用户榜
def au_top(request):
    au_list = cache.get('au_top_list')
    if not au_list:
        au_list = Member.objects.order_by('-au')[:20]
        cache.set('au_top_list',au_list,600)

    user_count = cache.get('user_count')
    if not user_count:
        user_count = Member.objects.all().count()
        cache.set('user_count',user_count,600)

    return render(request, "people/au_top.html", locals())

#用户发表文章
def user_topics(request, uid):
    this_user = Member.objects.get(pk=uid)
    topic_list = Topic.objects.order_by("-created_on").filter(author=uid)
    paginator = Paginator(topic_list, NUM_TOPICS_PER_PAGE)
    page = request.GET.get('page')
    try:
        topic_list = paginator.page(page)
    except PageNotAnInteger:
        topic_list = paginator.page(1)
    except EmptyPage:
        topic_list = paginator.page(paginator.num_pages)

    return render(request, "people/user_topics.html", locals())
    
# 用户个人页面 - 所有回复
def user_comments(request, uid):
    this_user = Member.objects.get(pk=uid)
    comment_list = Comment.objects.order_by("-created_on").filter(author=uid)
    paginator = Paginator(comment_list, NUM_COMMENT_PER_PAGE)
    page = request.GET.get('page')
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)

    return render(request, "people/user_comments.html", locals())
#邮箱验证功能
@login_required
@csrf_protect
def send_verified_email(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("user:settings"))

    user = request.user
    if user.email_verified:
        messages.error(request, u"您的邮箱已经验证过了")
        return HttpResponseRedirect(reverse("user:settings"))

    last_email = None
    try:
        last_email = Email.objects.get(user=user)
    except:
        pass

    if last_email and (timezone.now() - last_email.timestamp).seconds < (60):
        messages.error(request, u'一分钟内只能申请验证一次哦！')
    else:
        try:
            email = Email.objects.get(user=user)
            email.token = email.generate_token()
            email.timestamp = timezone.now()
            email.save()
        except Email.DoesNotExist:
            email = Email(user=user)
            email.token = email.generate_token()
            email.save()
        finally:
            send_mail(u"欢迎加入!", u"%s 你好：\r\n 欢迎您注册成为会员,请点击链接验证您的邮箱: %s%s" % 
                        (user.username,SITE_URL, reverse("user:email_verified", args=(user.id, email.token))),
                        "18636030403@163.com", [user.email]
                    )
            messages.success(request, u"邮件已经发送，请去您的邮箱验证一下您的邮箱，如果未收到邮件，请去垃圾信箱看一下。")
    return HttpResponseRedirect(reverse("user:settings"))

def email_verified(request, uid, token):
    try:
        user = Member.objects.get(pk=uid)
        email = Email.objects.get(user=user)
    except Member.DoesNotExist:
        raise Http404
    except Email.DoesNotExist:
        raise Http404
    else:
        if email.token == token:
            user.email_verified = True
            user.save()
            email.delete()
            messages.success(request, u"验证成功")
            if not request.user.is_authenticated():
                auth_login(request, user)
            return HttpResponseRedirect(reverse("question:index"))
        else:
            raise Http404


#邮件找回密码功能
def find_password(request):
    if request.method == "GET":
        return render(request, "people/find_password.html")

    email = request.POST["email"]
    user = None
    try:
        user = Member.objects.get(email=email)
    except Member.DoesNotExist:
        messages.error(request, '未找到用户')
    
    if user:
        find_pass = FindPass.objects.filter(user=user)
        if find_pass:
            find_pass = find_pass[0]
            if (timezone.now() - find_pass.timestamp).seconds < (60):
                messages.error(request, '一分钟内不能重复找回密码')
                return HttpResponseRedirect(reverse("question:index"))
        else:
            find_pass = FindPass(user=user)
            find_pass.timestamp = timezone.now()
            find_pass.token = find_pass.generate_token()

        find_pass.save()
        send_mail(u"重置密码", u"%s 你好：\r\n 请点击链接重置密码 %s%s" % (user.username,SITE_URL, reverse("user:first_reset_password", args=(user.id, find_pass.token))),
            "18636030403@163.com", [email]
                )
        messages.success(request, u"找回密码邮件已经发送，邮箱如果未收到邮件，请去垃圾信箱看一下。")
    
    return HttpResponseRedirect(reverse("question:index"))

def first_reset_password(request, uid=None, token=None):
    user = Member.objects.get(pk=uid)
    find_pass = FindPass.objects.filter(user=user)
    if not find_pass:
        messages.error(request, u"错误")
        return HttpResponseRedirect(reverse("user:find_pass"))
    find_pass = find_pass[0]

    now = timezone.now()
    timestamp = find_pass.timestamp
    if int(now.strftime('%Y%m%d'))-int(timestamp.strftime('%Y%m%d'))<3:
        request.session["find_pass"] = uid
        return render(request, "people/reset_password.html")
    else:
        raise Http404

def reset_password(request):
    if request.method == "GET":
        raise Http404

    password = request.POST.get("password", '')
    if len(password) < 6:
        messages.error(request, u"密码不能少于6位")
        return render(request, "people/reset_password.html")

    uid = request.session["find_pass"]
    user = Member.objects.get(pk=uid)
    if user:
        user.set_password(password)
        user.save()
        FindPass.objects.get(user=user).delete()
        del request.session["find_pass"]
        messages.success(request, u"重置成功，请登录")
        return HttpResponseRedirect(reverse("user:login"))

    raise Http404