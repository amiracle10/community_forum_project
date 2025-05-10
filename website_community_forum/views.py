from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.contrib.admin.views.decorators import staff_member_required
import json

from .models import Post, Reply, Category, Event
from .forms import RegisterForm
from django.contrib import messages
from .forms import ReportUserForm


def get_common_context():
    return {
        'online_users': [user for user in User.objects.all() if cache.get(f'seen_{user.id}') and now() - cache.get(f'seen_{user.id}') < timedelta(minutes=5)],
        'recent_posts': Post.objects.order_by('-created_at')[:5],
    }

def index(request):
    context = get_common_context()
    context['categories'] = Category.objects.all()
    popular_posts = Post.objects.annotate(comment_count=Count('replies')).order_by('-comment_count')[:3] 
    
    context['popular_posts'] = popular_posts
    return render(request, 'index.html', context)

def forum_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category).order_by('-created_at')
    context = get_common_context()
    context.update({
        'category': category,
        'posts': posts,
    })
    return render(request, 'forum_category.html', context)

def discussion_board(request):
    context = get_common_context()
    context['all_posts'] = Post.objects.all().order_by('-created_at')
    return render(request, 'discussions.html', context)

def about_board(request):
    return render(request, 'about.html', get_common_context())

def topics_board(request):
    context = get_common_context()
    context['posts'] = Post.objects.annotate(comment_count=Count('replies')).order_by('-comment_count')
    return render(request, 'topics.html', context)

def events_board(request):
    return render(request, 'events.html', get_common_context())

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session.set_expiry(0 if not remember_me else 60 * 60 * 24 * 30)
            return redirect('index')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password',
                'remember_checked': bool(remember_me),
            })
    return render(request, 'login.html', {'remember_checked': False})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def user_logout(request):
    if request.user.is_authenticated:
        cache.delete(f'seen_{request.user.id}')
        logout(request)
    return redirect('index')

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        data = json.loads(request.body)
        category = data.get('category')
        title = data.get('title')
        body = data.get('body')
        if not all([category, title, body]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        post = Post.objects.create(
            category=category,
            title=title,
            body=body,
            author=request.user,
        )
        return JsonResponse({'message': 'Post created', 'post_id': post.id}, status=201)
    return JsonResponse({'error': 'Invalid request'}, status=405)

@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        category_id = request.POST.get('category_id')
        if not all([title, body, category_id]):
            return redirect('/')
        category = get_object_or_404(Category, id=category_id)
        post = Post.objects.create(
            title=title,
            body=body,
            category=category,
            author=request.user,
        )
        return redirect('forum_category', category_slug=category.slug)
    return redirect('/')

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent_reply = Reply.objects.filter(id=parent_id).first() if parent_id else None
        Reply.objects.create(
            user=request.user,
            post=post,
            content=content,
            parent=parent_reply,
        )
        return redirect('post_detail', post_id=post.id)
    all_replies = Reply.objects.filter(post=post).select_related('user', 'parent').order_by('created_at')
    reply_map = {}
    top_level_replies = []
    for reply in all_replies:
        reply.temp_children = []
        reply_map[reply.id] = reply
        if reply.parent_id is None:
            top_level_replies.append(reply)
    for reply in all_replies:
        if reply.parent_id:
            parent = reply_map.get(reply.parent_id)
            if parent:
                parent.temp_children.append(reply)
    context = get_common_context()
    context.update({
        'post': post,
        'replies': top_level_replies,
    })
    return render(request, 'post_detail.html', context)

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden()
    if request.method == 'POST':
        post.delete()
        return redirect('forum_category', category_slug=post.category.slug)

def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user != reply.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        post_id = reply.post.id
        reply.delete()
        return redirect('post_detail', post_id=post_id)

def search_posts(request):
    query = request.GET.get('q')
    posts = Post.objects.filter(Q(title__icontains=query)).order_by('-created_at') if query else []
    context = get_common_context()
    context.update({
        'query': query,
        'posts': posts,
    })
    return render(request, 'search_results.html', context)

@login_required
def create_event(request):
    if request.method == 'POST':
        title = request.POST.get('name')
        description = request.POST.get('description')
        event_date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        has_end_time = request.POST.get('has_end_time') == 'on'
        end_time = request.POST.get('end_time') if has_end_time else None
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        Event.objects.create(
            title=title,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            has_end_time=has_end_time,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            approved=False,
        )

        return redirect('events')

    return redirect('events')

@staff_member_required
def review_events(request):
    context = get_common_context()
    context['pending_events'] = Event.objects.filter(approved=False)
    return render(request, 'review_events.html', context)

@staff_member_required
def approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.approved = True
    event.save()
    return redirect('review_events')

@staff_member_required
def reject_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('review_events')

@staff_member_required
def deny_event(request, event_id):
    Event.objects.get(pk=event_id).delete()
    return redirect('review_events')

def event_list(request):
    context = get_common_context()
    context['events'] = Event.objects.filter(approved=True).order_by('event_date', 'start_time')
    return render(request, 'events.html', context)


@login_required
def report_user(request, reported_user_id):
    reported_user = User.objects.get(id=reported_user_id)

    if request.method == 'POST':
        form = ReportUserForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.save()
            messages.success(request, 'Your report was submitted successfully. Thank you!')
            return redirect('index')
        else:
            messages.error(request, 'There was an error submitting the report.')
    else:
      form = ReportUserForm
    return render(request, 'report_user.html', {'form': form, 'reported_user': reported_user})