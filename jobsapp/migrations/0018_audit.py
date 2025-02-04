# Generated by Django 5.1.2 on 2025-01-27 09:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0017_alter_job_category_alter_job_company_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('INSERT', 'Insert'), ('UPDATE', 'Update'), ('DELETE', 'Delete')], max_length=10)),
                ('table_name', models.CharField(max_length=50)),
                ('record_id', models.IntegerField()),
                ('old_values', models.JSONField(blank=True, null=True)),
                ('new_values', models.JSONField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
