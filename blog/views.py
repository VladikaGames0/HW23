from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import BlogPost


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Только опубликованные статьи
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.views_count = F('views_count') + 1
        obj.save(update_fields=['views_count'])
        obj.refresh_from_db()
        return obj