from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0024_remove_sample_shipped'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='source',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Human', 'Human'),
                    ('Dog', 'Dog'),
                    ('Cat', 'Cat'),
                    ('Rat', 'Rat'),
                    ('Mouse', 'Mouse'),
                    ('Horse', 'Horse'),
                    ('Cow', 'Cow'),
                    ('Donkey', 'Donkey'),
                    ('Pig', 'Pig'),
                    ('Snake', 'Snake'),
                    ('Environment', 'Environment'),
                ],
                max_length=15,
                null=True,
            ),
        ),
    ]
