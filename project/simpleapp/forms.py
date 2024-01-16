from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Subscribers
from django.contrib.auth.models import User as auth_user

class PostForm(forms.ModelForm):
    class Meta:
       model = Post
       fields = ['title_of_post', 'author', 'post_text', 'category']


    def clean(self):
        cleaned_data = super().clean()
        post_text = cleaned_data.get("post_text")
        if post_text is not None and len(post_text) < 20:
            raise ValidationError({
                "post_text": "Заголовок не может быть менее 20 символов."
            })

        title_of_post = cleaned_data.get("title_of_post")
        if title_of_post == post_text:
            raise ValidationError(
                "Заголовок не должен быть идентичным тексту."
            )

        return cleaned_data


class SubscribersForm(forms.ModelForm):
    class Meta:
        model = Subscribers
        fields = ['category']
        labels = {
            'category': 'Категории'
        }

        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user')
            super(SubscribersForm, self).__init__(*args, **kwargs)
            subscribers = set(Subscribers.objects.filter(user=user).values_list('category__name', flat=True))
            self.fields.get('category').queryset = Category.objects.exclude(name__in=subscribers)
            if self.fields.get('category').queryset:
                self.fields.get('category').empty_label = 'Выберите категорию'
            else:
                self.fields.get('category').empty_label = 'Вы подписаны на все категории'
