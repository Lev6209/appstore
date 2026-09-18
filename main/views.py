from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from .models import App, Category, Review
from .forms import ReviewForm
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
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

    apps = apps.order_by(SORTS.get(sort, '-created_at'))

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
        context['form'] = ReviewForm()
        context['reviews'] = app.review_set.order_by('-created_at')
        return context


@require_POST
def add_review(request, app_id):
    app = get_object_or_404(App, id=app_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.app = app
        review.save()
        return redirect('main:app_detail', app_id=app.id)

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
        'price': app.price
    }
    return JsonResponse(data)