# Generated by Django 4.0.5 on 2022-08-11 05:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auction_users_watchlist_alter_auction_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bids',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
