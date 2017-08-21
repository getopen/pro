
from django import template
from django.conf import settings
import urllib.parse, hashlib
from django.contrib.auth import get_user_model

GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX",
                                      "http://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", "")
GRAVATAR_DEFAULT_RATING = getattr(settings, "GRAVATAR_DEFAULT_RATING", "g")
GRAVATAR_DEFAULT_SIZE = getattr(settings, "GRAVATAR_DEFAULT_SIZE", 80)

User = get_user_model()
register = template.Library()
#所有的标签和过滤器都是在这个实例中注册的
# ---Qiniu---

@register.simple_tag
#关于simple_tag检查所需 
def gravatar(user, size=None):
    try:
        if isinstance(user, User):
            return gravatar_url_for_user(user, size)
            #获取头像链接从用户
        return gravatar_url_for_email(user, size)
    except ValueError:
        raise template.TemplateSyntaxError("语法错误")

@register.simple_tag
def gravatar_url_for_user(user, size=None):
    if user.avatar and  user.avatar != '':
        #用户有头像 并且头像链接不为空
        img = 'http://ouiwyzbcj.bkt.clouddn.com/' + user.avatar
        #路径地址
        return img
        #并且返回头像地址
    else:
        email = _get_user(user)
        #如果用户没有头像，那么先获取到用户的邮箱地址
        return gravatar_url_for_email(email, size)
        #传递到gravatar_url_for_email函数继续获取

@register.simple_tag
def gravatar_url_for_email(email, size=None):
    gravatar_url = "%savatar/%s" % (GRAVATAR_URL_PREFIX,
            _get_gravatar_id(email))

    parameters = [p for p in (
        ('d', GRAVATAR_DEFAULT_IMAGE),
        ('s', size or GRAVATAR_DEFAULT_SIZE),
        ('r', GRAVATAR_DEFAULT_RATING),
    ) if p[1]]

    if parameters:
        gravatar_url += '?' + urllib.parse.urlencode(parameters, doseq=True)
        #urlencode == 's=48&r=g'
        #doseq=True -> &
    return gravatar_url
# >>> var
# [('s', (1, 2, 3)), ('r', 'g')]
# >>> urllib.parse.urlencode(var)
# 's=%281%2C+2%2C+3%29&r=g'
# >>> urllib.parse.urlencode(var,doseq=True)
# 's=1&s=2&s=3&r=g'

def _get_user(user):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise Exception("Bad user for gravatar.")
    return user.email

def _get_gravatar_id(email):
    email = email.encode()
    return hashlib.md5(email).hexdigest()






