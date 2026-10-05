from urllib import response

import form
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from .models import App, Category, Review
from .forms import ReviewForm, AppForm, RegisterForm, EditForm
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib import messages
from django.urls import reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView


SORTS = {
    'new': '-created_at',
    'name': 'name',
    'price': 'price',
    'expensive': '-price',
}

def index(request):
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'new')

    if q:
        apps = App.objects.filter(Q(name__icontains=q) | Q(description__icontains=q))
    else:
        apps = App.objects.all()

    apps = apps.select_related('author').order_by(SORTS.get(sort, '-created_at'))

    categories = Category.objects.all()

    paginator = Paginator(apps, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/index.html', {
        'q': q,
        'sort': sort,
        'page_obj': page_obj,
    })


# @require_GET
# def about(request):
#     return render(request, 'main/about.html')


class AboutView(TemplateView):
    template_name = 'main/about.html'



# def app_detail(request, app_id):
#     app = get_object_or_404(App, id=app_id)
#     similar_apps = App.objects.filter(price__gte=app.price - 10, price__lte=app.price + 10).exclude(id=app.id)[:3]
#     return render(request,'main/app_detail.html',{'app': app, 'similar_apps': similar_apps})

class AppDetailView(DetailView):
    model = App
    template_name = 'main/app_detail.html'
    context_object_name = 'app'
    pk_url_kwarg = 'app_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = self.object
        context['similar_apps'] = (
            App.objects.filter(
                price__gte=app.price - 10,
                price__lte=app.price + 10
            )
            .exclude(id=app.id)[:3]
        )
        form = ReviewForm()
        if self.request.user.is_authenticated and 'username' in form.fields:
            form.fields.pop('username')
        context['form'] = form
        context['reviews'] = app.review_set.order_by('-created_at')
        return context


@require_POST
def add_review(request, app_id):
    app = get_object_or_404(App, id=app_id)
    data = request.POST.copy()
    if request.user.is_authenticated:
        data['username'] = request.user.username
    form = ReviewForm(data)

    if form.is_valid():
        review = form.save(commit=False)
        review.app = app
        review.save()
        messages.success(request,'Отзыв сохранён')
        return redirect('main:app_detail', app_id=app.id)

    if request.user.is_authenticated and 'username' in form.fields:
        form.fields.pop('username')

    reviews = app.review_set.order_by('-created_at')
    similar_apps = (
        App.objects.filter(
            price__gte=app.price - 10,
            price__lte=app.price + 10
        )
        .exclude(id=app.id)[:3]
    )
    return render(request, 'main/app_detail.html', {
        'app': app,
        'form': form,
        'reviews': reviews,
        'similar_apps': similar_apps,
    })


# def category_detail(request, category_id):
#     category = get_object_or_404(Category, id=category_id)
#     apps = App.objects.filter(category=category)
#     expensive = App.objects.filter(price__isnull=False, price__gt=0,category=category).order_by('-price').first()
#     return render(request, 'main/category.html', {
#         'category': category,
#         'apps': apps,
#         'expensive': expensive
#     })

class CategoryDetailView(ListView):
    model = App
    template_name = 'main/category.html'
    context_object_name = 'apps'

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return App.objects.filter(category_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = Category.objects.get(id=category_id)
        expensive = App.objects.filter(
            price__isnull=False,
            price__gt=0,
            category_id=category_id
        ).order_by('-price').first()

        context['category'] = category
        context['expensive'] = expensive
        return context


# def new(request):
#     apps = App.objects.order_by('-created_at')[:5]
#     return render(request, 'main/new.html', {'apps': apps})

class NewAppView(ListView):
    model = App
    template_name = 'main/new.html'
    context_object_name = 'apps'
    ordering = ['-created_at']
    paginate_by = 3

def top(request):
    apps = App.objects.order_by('-price').exclude(price=0)[:10]
    return render(request, 'main/top.html', {'apps': apps})

def free(request):
    apps = App.objects.filter(price=0)
    return render(request, 'main/free.html', {'apps': apps})

def free_in_category(request, category_id):
    apps = App.objects.filter(price=0, category_id=category_id)
    return render(request, 'main/free.html', {'apps': apps})

def no_category(request):
    apps = App.objects.filter(category=None)
    return render(request, 'main/no_category.html', {'apps': apps})

def cheap(request):
    apps = App.objects.order_by('price').filter(price__lt=100, price__gt=0)[:10]
    return render(request, 'main/cheap.html', {'apps': apps})

def developer(request, developer_name):
    return HttpResponse(f'Страница разработчика: {developer_name}')

def secure_app(request, unique_key):
    return HttpResponse(f'Защищенное приложение с уникальным ключом: {unique_key}')


# def apps_list(request,is_free):
#     if is_free:
#         apps = App.objects.filter(price=0)
#         title = "Бесплатные приложения"
#     else:
#         apps = App.objects.filter(price__gt=0)
#         title = "Платные приложения"
#     return render(request, 'main/apps_list.html', {'apps': apps, 'title': title})


class AppsListView(ListView):
    model = App
    template_name = 'main/apps_list.html'
    context_object_name = 'apps'

    def get_queryset(self):
        if self.kwargs['is_free']:
            return App.objects.filter(price=0)
        else:
            return App.objects.filter(price__gt=0)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs['is_free']:
            context['title'] = 'Бесплатные приложения'
        else:
            context['title'] = 'Платные приложения'
        return context

def api_app_detail(request, app_id):
    app = get_object_or_404(App, id=app_id)
    data = {
        'id': app.id,
        'name': app.name,
        'description': app.description,
        'price': app.price,
        'icon': app.icon.url if app.icon else None,
    }
    return JsonResponse(data)

@login_required
def add_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.author = request.user
            app.save()
            messages.success(request, f"Приложение {app.name} опубликовано.")
        return redirect('main:app_detail', app_id=app.id)
    else:
        form = AppForm()
    return render(request, 'main/add_app.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Аккаунт создан.')
            return redirect('main:index')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


class StoreLoginView(LoginView):
    template_name = 'main/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'С возвращением, {self.request.user.username}!')
        return response

class StoreLogoutView(LogoutView):
    next_page = reverse_lazy('main:index')

@login_required
def my_apps(request):
    apps = App.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'main/my_apps.html', {'apps': apps})

@login_required
def edit_app(request, app_id):
    app = get_object_or_404(App, id=app_id)
    if not (
        request.user.has_perm('main.change_app')
        or request.user.is_staff
        or app.author_id == request.user.id
    ):
        messages.error(request, 'Редактировать карточку приложения может только его автор')
        return redirect('main:app_detail', app_id=app.id)

    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            app = form.save(commit=False)
            app.author = request.user
            app.save()
            messages.success(request, f"Карточка приложения {app.name} обновлена успешно.")
            return redirect('main:app_detail', app_id=app.id)
    else:
        form = AppForm(instance=app)
    return render(request, 'main/edit_app.html', {'form': form, 'app': app})

@login_required
def admin_edit_app(request, app_id):
    app = get_object_or_404(App, id=app_id)

    if not request.user.is_superuser:
        messages.error(
            request,
            'Редактировать автора может только администратор'
        )
        return redirect('main:app_detail', app_id=app.id)

    if request.method == 'POST':
        form = EditForm(
            request.POST,
            request.FILES,
            instance=app
        )

        if form.is_valid():
            app = form.save()

            messages.success(
                request,
                f"Карточка приложения {app.name} обновлена успешно."
            )
            return redirect('main:app_detail', app_id=app.id)

    else:
        form = EditForm(instance=app)

    return render(
        request,
        'main/edit_app.html',
        {
            'form': form,
            'app': app
        }
    )

class StorePasswordResetView(PasswordResetView):
    template_name = 'main/password_reset_form.html'
    email_template_name = 'main/password_reset_email.html'
    subject_template_name = 'main/password_reset_subject.txt'
    success_url = reverse_lazy('main:password_reset_done')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'].label = 'Электронная почта'
        return form


class StorePasswordResetDoneView(PasswordResetDoneView):
    template_name = 'main/password_reset_done.html'


class StorePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'main/password_reset_confirm.html'
    success_url = reverse_lazy('main:password_reset_complete')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if form is not None and 'new_password1' in form.fields:
            form.fields['new_password1'].label = 'Новый пароль'
            form.fields['new_password2'].label = 'Повтор пароль'
        return form


class StorePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'main/password_reset_complete.html'

