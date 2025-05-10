from django.contrib import admin
from .models import Post, Category, Reply, Event
from .models import UserReport

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'body')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('content',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'city', 'state', 'approved')
    list_filter = ('approved', 'event_date')
    search_fields = ('title', 'description', 'city', 'state')
    actions = ['approve_selected']

    @admin.action(description="Approve selected events")
    def approve_selected(self, request, queryset):
        queryset.update(approved=True)

class UserReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'reason', 'created_at')
    list_filter = ('created_at', 'reporter', 'reported_user')

admin.site.register(UserReport)