from django import template

register = template.Library()

@register.filter
def stars(value):
    full = int(value)
    return '★' * full + '☆' * (5 - full)

@register.filter
def reviews_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'отзывов'
    elif value % 10 == 1:
        word = 'отзыв'
    elif 2 <= value % 10 <= 4:
        word = 'отзыва'
    else:
        word = 'отзывов'

    return f'{value} {word}'

@register.filter
def categories_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'категорий'
    elif value % 10 == 1:
        word = 'категория'
    elif 2 <= value % 10 <= 4:
        word = 'категории'
    else:
        word = 'категорий'

    return f'{value} {word}'

@register.filter
def apps_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'приложений'
    elif value % 10 == 1:
        word = 'приложение'
    elif 2 <= value % 10 <= 4:
        word = 'приложения'
    else:
        word = 'приложений'

    return f'{value} {word}'