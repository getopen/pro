from django.db import models
from people.models import Member as User
from django.db.models.signals import post_save

#类别表
class Category(models.Model):
    name = models.CharField(max_length=100,verbose_name='类别名称')
    def __str__(self):
        return self.name
#节点表
class Node(models.Model):
    name = models.CharField(max_length=100,verbose_name='节点名称')
    slug = models.SlugField(max_length=100,verbose_name='url标识符')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_on = models.DateTimeField(blank=True, null=True,auto_now=True,verbose_name='更新时间')
    num_topics = models.IntegerField(default=0,verbose_name='主题数')
    category = models.ForeignKey(Category,verbose_name='所属类别')
    def __str__(self):
        return self.name
#主题表
class Topic(models.Model):
    title = models.CharField(max_length=100,verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    node = models.ForeignKey(Node,verbose_name='所属节点')
    author = models.ForeignKey(User,verbose_name='作者')
    num_views = models.IntegerField(default=0,verbose_name='浏览量')
    num_comments = models.IntegerField(default=0,verbose_name='评论数')
    num_favorites = models.IntegerField(default=0,verbose_name='收藏数')
    last_reply = models.ForeignKey(User,related_name='+',verbose_name='最后回复者')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='发表时间')
    updated_on = models.DateTimeField(blank=True, null=True,verbose_name='更新时间')
    def __str__(self):
        return self.title
#评论表
class Comment(models.Model):
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User,verbose_name='作者')
    topic = models.ForeignKey(Topic,verbose_name='所属主题')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='评论时间')
    def __str__(self):
        return self.content
#消息通知表
class Notice(models.Model):
    from_user = models.ForeignKey(User,related_name='+',verbose_name='来自用户')   #not to create a backwards relation
    to_user = models.ForeignKey(User,related_name='+',verbose_name='接收用户')
    topic = models.ForeignKey(Topic,null=True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    is_readed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.content
#用户最爱文章
class FavoritedTopic(models.Model):
    user = models.ForeignKey(User, verbose_name="用户")
    topic = models.ForeignKey(Topic, verbose_name="主题")
    #class Meta:
        #unique_together = ('user', 'topic')
    def __str__(self):
        return str(self.id)
#信号捕捉
def create_notice(sender, **kwargs):
    #{'signal': <django.db.models.signals.ModelSignal object at 0x000001A035038080>, 
    #'instance': <Comment: 就是棒>, 
    #'created': True, 
    #'update_fields': None, 
    #'raw': False, 
    #'using': 'default'}
    comment = kwargs['instance']
    if comment.author != comment.topic.author:      # don't create notice when you reply to yourself
        Notice.objects.create(from_user=comment.author,to_user=comment.topic.author,topic=comment.topic,content=comment.content)
#只要是涉及到comment的添加操作都会导致这个信号post_save触发
#关于Comment的信号我们将在处理之前先进行这个函数的判断
#如果评论者不是主题所有者，那么在notice表中把评论消息作为通知存储
#信号的格式为一个字典，其中的instance代表当前触发信号的实例对象
post_save.connect(create_notice, sender=Comment)
