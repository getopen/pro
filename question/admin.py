from django.contrib import admin

# Register your models here.
from django.contrib import admin
from question.models import Topic, Comment, Category, Node, Notice, FavoritedTopic

class TopicAdmin(admin.ModelAdmin):
	list_display = ('id','title','created_on','node','author','num_comments','num_views')
	search_fields = ['title']
	list_filter = ('node__name',)

class CommentAdmin(admin.ModelAdmin):
	list_display = ('content', 'topic', 'author','created_on',)
	list_filter = ('topic__node__name',)

class NodeAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug' , 'category' ,'created_on', 'updated_on', 'num_topics')

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)

class NoticeAdmin(admin.ModelAdmin):
	list_display = ('from_user', 'to_user','topic','is_readed','is_deleted','time')

admin.site.register(Topic, TopicAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(FavoritedTopic)