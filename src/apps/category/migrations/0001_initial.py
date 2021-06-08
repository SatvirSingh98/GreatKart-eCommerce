# Generated by Django 3.2.4 on 2021-06-05 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, upload_to='images/categories/')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
    ]
