# Generated by Django 2.1.2 on 2018-12-11 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingapp', '0009_auto_20181210_0412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profileImage',
            field=models.ImageField(blank=True, null=True, upload_to='profileimage'),
        ),
    ]