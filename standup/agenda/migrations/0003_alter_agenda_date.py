# Generated by Django 4.2.5 on 2023-10-05 02:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0002_alter_agenda_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agenda",
            name="date",
            field=models.CharField(
                default="2023-10-04", primary_key=True, serialize=False, unique=True
            ),
        ),
    ]
