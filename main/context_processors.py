from django.db.models import Count

from . import apps
from .models import App, Category, Review


def store_menu(request):
    categories = list(
        Category.objects
        .annotate(apps_count=Count('app')).filter(apps_count__gt=0)
        .order_by('name')
    )
    return {
        'categories': categories,
        'apps_total': App.objects.count(),
        'categories_total': len(categories),
        'reviews_total': Review.objects.count(),
    }