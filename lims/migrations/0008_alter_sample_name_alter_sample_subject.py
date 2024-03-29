# Generated by Django 4.2.5 on 2024-01-02 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0007_subject_family_name_alter_subject_given_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='name',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='lims.subject'),
        ),
    ]
