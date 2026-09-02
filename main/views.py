from django.shortcuts import render, get_object_or_404

from .models import App

from .models import Category

from django.http import HttpResponse





def index(request):
    apps = App.objects.order_by('-created_at').all()
    featured = App.objects.order_by('-price').first()
    categories = Category.objects.all()
    return render(request, 'main/index.html', {
        'apps': apps,
        'featured': featured,
        'categories': categories,
    })


def about(request):
    return render(request, 'main/about.html')


def app_detail(request, app_id):
    app = get_object_or_404(App, id=app_id)
    similar_apps = App.objects.filter(price__gte=app.price - 30, price__lte=app.price + 30).exclude(id=app.id)[:3]
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




