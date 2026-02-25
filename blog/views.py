from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import F
from django.contrib import messages

from .models import BlogPost


class BlogPostListView(ListView):
    """Список блоговых записей"""
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        # Только опубликованные статьи
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context


class BlogPostDetailView(DetailView):
    """Детальная страница блоговой записи"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров для всех пользователей
        obj.views_count = F('views_count') + 1
        obj.save(update_fields=['views_count'])
        obj.refresh_from_db()
        return obj


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой блоговой записи"""
    model = BlogPost
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('blog:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Запись успешно создана!')
        return super().form_valid(form)


class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование блоговой записи"""
    model = BlogPost
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'preview', 'is_published']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context

    def get_success_url(self):
        messages.success(self.request, 'Запись успешно обновлена!')
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление блоговой записи"""
    model = BlogPost
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Запись успешно удалена!')
        return super().delete(request, *args, **kwargs)