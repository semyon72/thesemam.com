# Generated by Django 3.1.2 on 2021-05-21 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20210521_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='blog',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='entry',
            name='headline',
            field=models.CharField(max_length=256),
        ),
    ]