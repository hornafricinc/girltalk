# Generated by Django 3.0.3 on 2020-04-20 06:19

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
            name='SubscriberDetails',
            fields=[
                ('txn_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('s_plan', models.CharField(max_length=4)),
                ('amount', models.DecimalField(decimal_places=4, max_digits=10)),
                ('payer_email', models.CharField(max_length=50)),
                ('subscription_date', models.DateTimeField()),
                ('due_date', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'subscriptions',
            },
        ),
        migrations.CreateModel(
            name='ClientSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
