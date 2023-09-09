# Generated by Django 4.2.5 on 2023-09-09 12:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0006_alter_item_date_resolved"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agenda",
            name="date",
            field=models.CharField(
                default="2023-09-09", primary_key=True, serialize=False, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="link_to_ticket",
            field=models.URLField(default="", null=True),
        ),
    ]