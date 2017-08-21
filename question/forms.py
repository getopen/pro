from django import forms
from question.models import Topic, Comment

class TopicForm(forms.ModelForm):
    title = forms.CharField(label='标题',required=True)
    content = forms.CharField(label='内容',required=False)
    def clean_title(self):
        title = self.cleaned_data.get("title").strip()
        if len(title) < 3:
            raise forms.ValidationError("标题太短哦...")
        elif len(title) > 100:
            raise forms.ValidationError("标题太长哦...")
        else:
            return title
    def clean_content(self):
        content = self.cleaned_data.get("content").strip()
        if len(content) > 5000:
            raise forms.ValidationError("正文内容太长哦...")
        else:
            return content
    class Meta:
        model = Topic
        fields = ('title','content')

class ReplyForm(forms.ModelForm):
    content = forms.CharField(label=u'回复',required=False)
    def clean_content(self):
        content = self.cleaned_data.get("content").strip()
        if len(content) == 0:
            raise forms.ValidationError("请输入评论内容...")
        elif len(content) > 800:
            raise forms.ValidationError("评论内容太长哦...")
        else:
            return content
    class Meta:
        model = Comment
        fields = ('content',)

class AboutForm(forms.Form):
    url = forms.CharField(label=u'你要爬取的百度图片链接:',required=False)
    def clean_url(self):
        url = self.cleaned_data.get('url').strip()
        if 'baidu' not in url:
            raise forms.ValidationError("请输入正确的百度云链接...")
        else:
            return url