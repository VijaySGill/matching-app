# Generated by Django 2.1.2 on 2018-12-07 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingapp', '0006_auto_20181206_0235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profileImage',
            field=models.ImageField(blank=True, null=True, upload_to='profile_image'),
        ),
    ]