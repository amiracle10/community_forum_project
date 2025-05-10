"""
URL configuration for community_forum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from website_community_forum import views
from website_community_forum.views import (
    index, forum_category, discussion_board, event_list,
    topics_board, about_board, user_logout, user_login, register, post_detail, delete_post,
    delete_reply, search_posts,
    create_event, review_events, approve_event, deny_event
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('forum/<slug:category_slug>/', views.forum_category, name='forum_category'),
    path('discussions/', views.discussion_board, name='discussions'),
    path('events/', event_list, name='events'),  # ✅ Esta línea fue actualizada
    path('topics/', views.topics_board, name='topics'),
    path('about/', views.about_board, name='about'),
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),

    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('search/', search_posts, name='search'),

    path('events/create/', create_event, name='create_event'),
    path('events/review/', review_events, name='review_events'),
    path('events/approve/<int:event_id>/', approve_event, name='approve_event'),
    path('events/deny/<int:event_id>/', deny_event, name='deny_event'),
    path('report_user/<int:reported_user_id>/', views.report_user, name='report_user'),
]
