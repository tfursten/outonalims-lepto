# Generated by Django 5.0.1 on 2025-03-06 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0013_test_lab'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='lab',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
