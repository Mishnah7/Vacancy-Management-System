# Generated by Django 5.1.2 on 2025-01-27 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0016_importerror'),
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='company_description',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='company_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='last_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='location',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='posting_type',
            field=models.CharField(blank=True, choices=[('internal', 'Internal Only'), ('external', 'External Only'), ('both', 'Both Internal and External')], default='external', max_length=10),
        ),
        migrations.AlterField(
            model_name='job',
            name='salary',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='tags',
            field=models.ManyToManyField(blank=True, to='tags.tag'),
        ),
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Full time'), ('2', 'Part time'), ('3', 'Internship')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='vacancy',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='website',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
