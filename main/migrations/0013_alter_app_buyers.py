from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_app_buyers_purchase'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='buyers',
        ),

        migrations.AddField(
            model_name='app',
            name='buyers',
            field=models.ManyToManyField(
                related_name='purchased_apps',
                through='main.Purchase',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Купили',
            ),
        ),
    ]