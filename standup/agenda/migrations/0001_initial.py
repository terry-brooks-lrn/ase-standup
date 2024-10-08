# Generated by Django 4.2.15 on 2024-09-06 19:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import martor.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportEngineer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("username", models.CharField(max_length=255)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Support Engineer",
                "verbose_name_plural": "Support Engineers",
                "db_table": "team_members",
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="SupportMail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "edition",
                    models.CharField(
                        choices=[
                            ("1", "January"),
                            ("2", "February"),
                            ("3", "March"),
                            ("4", "April"),
                            ("5", "May"),
                            ("6", "June"),
                            ("7", "July"),
                            ("8", "August"),
                            ("9", "September"),
                            ("10", "October"),
                            ("11", "November"),
                            ("12", "December"),
                        ],
                        max_length=3,
                    ),
                ),
                ("year", models.IntegerField(default=2024)),
            ],
            options={
                "verbose_name": "Support Mail Edition",
                "verbose_name_plural": "Support Mail Editions",
                "db_table": "support_mail_editions",
                "ordering": ["-year", "edition"],
            },
        ),
        migrations.CreateModel(
            name="WIN_OOPS",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_occurred", models.DateField(auto_now=True)),
                ("type_of_incident", models.CharField(choices=[("WIN", "Win!"), ("OOPS", "Oops")], max_length=5)),
                ("clients_involved", models.CharField(max_length=255, null=True)),
                ("description", martor.models.MartorField()),
                ("added_to_supportmail", models.BooleanField(default=False)),
                (
                    "reported_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "verbose_name": "Win and Mistake",
                "verbose_name_plural": "Wins and Mistakes",
                "db_table": "wins_mistakes",
                "ordering": ["-date_occurred"],
            },
        ),
        migrations.CreateModel(
            name="Update",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_created", models.DateField(auto_now_add=True)),
                ("date_of_event", models.DateField()),
                ("description", models.CharField(max_length=65535)),
                ("ticket", models.URLField(blank=True, null=True)),
                (
                    "added_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "verbose_name": "Update",
                "verbose_name_plural": "Updates",
                "db_table": "personal_updates",
                "ordering": ["-date_created"],
            },
        ),
        migrations.CreateModel(
            name="ClientCall",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_created", models.DateField(auto_now_add=True)),
                ("date_of_event", models.DateField()),
                ("topic", models.CharField(max_length=65535)),
                ("client", models.CharField(max_length=65535)),
                ("ticket", models.URLField(blank=True, null=True)),
                (
                    "leading_call",
                    models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "verbose_name": "Client Call",
                "verbose_name_plural": "Client Calls",
                "db_table": "client_calls",
                "ordering": ["-date_of_event"],
            },
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_created", models.DateField(auto_now_add=True)),
                ("date_resolved", models.DateField(blank=True, null=True)),
                ("last_modified", models.DateTimeField(auto_now=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "New"),
                            ("OPEN", "Open"),
                            ("FYI", "Visibility Only"),
                            ("RESOLVED", "Resolved"),
                            ("PUBLISHED", "Published"),
                            ("ACCEPTED", "Feature Accepted"),
                            ("REJECTED", "Feature Rejected"),
                            ("BACKLOG", "Feature Pending"),
                        ],
                        default="NEW",
                        max_length=65535,
                    ),
                ),
                (
                    "section",
                    models.CharField(
                        choices=[
                            ("REVIEW", "Ticket Help or Review"),
                            ("MONITOR", "Ticket Monitoring"),
                            ("FOCUS", "Client's Need Focus or Attention"),
                            ("CALLS", "Upcoming Client Calls"),
                            ("INTERNAL", "Internal Tasks"),
                            ("NEEDS", "Team, Departmental, Organizational Needs"),
                            ("UPDATES", "Personal, Social Updates"),
                            ("MISC", "Miscellaneous"),
                            ("DOCS", "Documentation Review and Enhancement"),
                            ("IFEAT", "internal Feature Requests"),
                        ],
                        max_length=65535,
                    ),
                ),
                ("title", models.CharField(default="", max_length=65535)),
                ("link_to_ticket", models.URLField(blank=True, default="", null=True)),
                ("description", martor.models.MartorField()),
                ("notes", martor.models.MartorField(blank=True, default="", null=True)),
                ("next_task_needed_to_resolve", models.CharField(blank=True, max_length=65535, null=True)),
                ("added_to_supportmail", models.BooleanField(default=False)),
                ("added_to_supportmail_on", models.DateField(blank=True, null=True)),
                (
                    "creator",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "owner_of_next_task_needed_to_resolve",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="item_task_owner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supportmail_edition",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="agenda.supportmail"
                    ),
                ),
            ],
            options={
                "verbose_name": "Agenda Item",
                "verbose_name_plural": "Agenda Item",
                "db_table": "items",
                "ordering": ["-date_created"],
                "indexes": [
                    models.Index(fields=["date_created"], name="items_date_cr_753d2d_idx"),
                    models.Index(fields=["date_created", "section", "status"], name="items_date_cr_69ea7e_idx"),
                    models.Index(fields=["creator", "section", "status"], name="items_creator_da63da_idx"),
                    models.Index(
                        fields=["added_to_supportmail", "added_to_supportmail_on"], name="items_added_t_003926_idx"
                    ),
                    models.Index(fields=["last_modified", "section", "status"], name="items_last_mo_ae8bed_idx"),
                    models.Index(fields=["last_modified", "status"], name="items_last_mo_df1974_idx"),
                    models.Index(fields=["last_modified"], name="items_last_mo_4acfb1_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Agenda",
            fields=[
                ("date", models.CharField(default="2024-09-06", primary_key=True, serialize=False, unique=True)),
                (
                    "driver",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="driver",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "notetaker",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="notetaker",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Agenda",
                "verbose_name_plural": "Agendas",
                "db_table": "agendas",
                "ordering": ["-date"],
                "get_latest_by": ["date"],
                "indexes": [
                    models.Index(fields=["date"], name="agendas_date_7addc9_idx"),
                    models.Index(fields=["driver"], name="agendas_driver__680be4_idx"),
                    models.Index(fields=["notetaker"], name="agendas_notetak_bcc76d_idx"),
                ],
            },
        ),
    ]
