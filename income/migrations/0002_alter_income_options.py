# Generated by Django 3.2.6 on 2021-08-31 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='income',
            options={'ordering': ['-date']},
        ),
    ]
