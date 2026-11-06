from django.db.models import Count
from django.core.cache import cache

from . import apps
from .models import App, Category, Review
from .views import favorites


def store_menu(request):
    categories = cache.get('menu_categories')
    if categories is None:
        categories = list(
            Category.objects
            .annotate(apps_count=Count('app')).filter(apps_count__gt=0)
            .order_by('name')
        )
        cache.set('menu_categories', categories, 60 * 3)

    apps_total = cache.get('apps_total')

    if apps_total is None:
        apps_total = App.objects.count()
        cache.set('apps_total', apps_total, 60 * 10)

    favorites_count = 0
    if request.user.is_authenticated:
        favorites_count = request.user.favorite_apps.count()

    featured = App.objects.order_by('-price').first()

    return {
        'categories': categories,
        'apps_total': apps_total,
        'categories_total': len(categories),
        'reviews_total': Review.objects.count(),
        'featured': featured,
        'favorites_count': favorites_count,

    }