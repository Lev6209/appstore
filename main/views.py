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
    return render(request, 'main/app_detail.html', {'app': app})


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    apps = App.objects.filter(category=category)
    return render(request, 'main/category.html', {'category': category, 'apps': apps})


def new(request):
    apps = App.objects.order_by('-created_at')[:5]
    return render(request, 'main/new.html', {'apps': apps})