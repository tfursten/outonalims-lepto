# Generated by Django 5.0.1 on 2025-03-10 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0022_remove_sampleresult_run_rep_sampleresult_run_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sampleresult',
            name='dye',
        ),
        migrations.AddField(
            model_name='sample',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sample',
            name='shipped_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
