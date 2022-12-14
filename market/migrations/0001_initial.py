# Generated by Django 2.2.1 on 2022-11-22 10:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('balance', models.PositiveIntegerField(default=20000)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.PositiveIntegerField(default=0)),
                ('status', models.IntegerField(choices=[(1, 'در حال خرید'), (2, 'ثبت\u200cشده'), (3, 'لغوشده'), (4, 'ارسال\u200cشده')])),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('price', models.PositiveIntegerField()),
                ('inventory', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='OrderRow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.Product')),
            ],
        ),
    ]
