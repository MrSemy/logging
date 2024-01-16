from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from datetime import datetime
from project import settings
from .models import Post, Subscribers
from .filters import PostFilter
from django.urls import reverse_lazy
from .forms import PostForm, SubscribersForm
from django.db.models.signals import post_save
from .tasks import send_mail_after_news_post
from .mixins import UserToFormMixin


def notify_about_new_post(sender, **kwargs):
    for user in Subscribers.objects.filter(category=kwargs['instance'].category):
        send_mail(
            subject='Новый пост',
            message=f'Новый пост в категории {kwargs["instance"].category}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,)


post_save.connect(notify_about_new_post, sender=Post)

class ProtectedPostsView(LoginRequiredMixin, ListView):
    template_name = 'posts.html'


class PostsList(ListView):
    model = Post
    ordering = '-date_of_post'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10


    def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostFilter(self.request.GET, queryset)
       return self.filterset.qs

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       # Добавляем в контекст объект фильтрации.
       context['filterset'] = self.filterset
       return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'simpleapp.add_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    send_mail_after_news_post()

    def form_valid(self, form):
        post = form.save(commit=False)
        post.news_or_article = 'news'
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'simpleapp.change_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'simpleapp.delete_post'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'simpleapp.add_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.news_or_article = 'article'
        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'simpleapp.change_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class ArticleDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'simpleapp.delete_post'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')


class MyView(PermissionRequiredMixin, ListView):
    permission_required = 'protect.view_post'


class SubscribersView(CreateView):
    model = Subscribers
    form_class = SubscribersForm
    template_name = 'Subscribe.html'
    success_url = '/subscribe/'

    def form_valid(self, form):
        subscriber = form.save(commit=False)
        if self.request.method == 'POST':
            form.instance.user = self.request.user
        subscriber.save()
        send_mail(
            subject='Подписка на категорию',
            message=f'Вы подписались на новости из категории { form.instance.category }',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.request.user.email],
        )
        return super().form_valid(form)
