# Generated by Django 6.0.dev20250307143456 on 2025-04-12 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChessGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.CharField(choices=[('white', 'White'), ('black', 'Black')], default='white', max_length=5)),
                ('board', models.JSONField(default=dict)),
            ],
        ),
    ]
