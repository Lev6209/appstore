from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import App, Category
from django.db.models import Q
from django.http import HttpResponse

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
    featured = App.objects.order_by('-price').first()
    categories = Category.objects.all()

    paginator = Paginator(apps, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/index.html', {
        'q': q,
        'sort': sort,
        'page_obj': page_obj,
        'featured': featured,
        'categories': categories,
    })


def about(request):
    return render(request, 'main/about.html')


def app_detail(request, app_id):
    app = get_object_or_404(App, id=app_id)
    similar_apps = App.objects.filter(price__gte=app.price - 10, price__lte=app.price + 10).exclude(id=app.id)[:3]
    return render(request,'main/app_detail.html',{'app': app, 'similar_apps': similar_apps})


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    apps = App.objects.filter(category=category)
    expensive = App.objects.filter(price__isnull=False, price__gt=0,category=category).order_by('-price').first()
    return render(request, 'main/category.html', {'category': category, 'apps': apps, 'expensive': expensive})


def new(request):
    apps = App.objects.order_by('-created_at')[:5]
    return render(request, 'main/new.html', {'apps': apps})

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


def app_list(request,is_free):
    if is_free:
        message = "Список бесплатных приложений"
    else:
        message = "Список платных приложений"
    return HttpResponse(message)