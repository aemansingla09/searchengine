# Generated by Django 4.1.3 on 2022-12-04 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userapp", "0002_alter_siteindexer_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitelinks",
            name="url",
            field=models.URLField(),
        ),
        migrations.AlterUniqueTogether(
            name="sitelinks",
            unique_together={("url", "site_id")},
        ),
    ]
