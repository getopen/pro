from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from people.models import Member, Follower


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)
    class Meta:
        model = Member
        fields = ('email', 'username')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次输入验证失败")
        return password2
    #在form中的clean__field函数会在is_valid()函数验证时自动调用
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        #set_password将会采用django的加密算法将密码设置到对应的模型实例中
        #在内存中创建的好的对象只有通过commit=True才被真正执行到数据库上
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = Member
        fields = ('email', 'password', 'username', 'is_active', 'is_admin',)
    def clean_password(self):
        return self.initial["password"]
    #使用默认的save函数即可

class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'email', 'username', 'email_verified', 'last_login','is_active','is_admin','last_ip')
    list_display_links = ('id', 'email', 'username')
    list_filter = ('email', 'email_verified',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'date_joined', 'password','is_active','is_admin','avatar')}),
        ('状态', {'fields': ('email_verified', 'last_ip', 'au', 'topic_num', 'comment_num')}),
        ('社交网络', {'fields': ('weibo_id', 'blog')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            #admin样式设置
            #Fieldsets 使用 wide 样式将会有额外的水平空格.
            'fields': ('email', 'username', 'password1', 'password2','is_active','is_admin')}
        ),
    )
    search_fields = ('id', 'email', 'username')
    ordering = ('id', 'email', 'email_verified')
    filter_horizontal = ()
    #这个字段为了设置与groups关联的多选框
admin.site.register(Member, MyUserAdmin)
admin.site.register(Follower)