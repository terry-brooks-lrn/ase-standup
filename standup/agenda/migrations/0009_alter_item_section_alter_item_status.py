# Generated by Django 4.2.5 on 2023-09-09 12:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0008_alter_item_section_alter_item_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="section",
            field=models.CharField(
                choices=[
                    ("REVIEW", "Ticket Help or Review"),
                    ("MONITOR", "Ticket Monitoring"),
                    ("FOCUS", "Client's Need Focus or Attention"),
                    ("CALLS", "Upcoming Client Calls"),
                    ("INTERNAL", "Internal Tasks"),
                    ("NEEDS", "Team, Departmental, Organizaional Needs"),
                    ("UPDATES", "Personal, Social Updates"),
                    ("MISC", "Miscellaneous"),
                ],
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="status",
            field=models.CharField(
                choices=[
                    ("NEW", "New"),
                    ("OPEN", "Open"),
                    ("FYI", "Visibility Only"),
                    ("RESOLVED", "Resolved"),
                ],
                default="NEW",
                max_length=255,
            ),
        ),
    ]