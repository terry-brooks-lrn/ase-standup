import datetime
import os
import random

import arrow
import json 
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from logtail import LogtailHandler
from martor.models import MartorField
from django.db.models import QuerySet
from loguru import logger
from django.db.models import Q
from django.db.models.constraints import CheckConstraint
from agenda.errors import AgendaItemClassificationError
from django.contrib.auth.base_user import BaseUserManager
from agenda.errors import DuplicateUsernameError
from prometheus_client import Histogram

NOW = arrow.now(tz="America/Chicago").format("YYYY-MM-DD")

PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")

supportmail_generation_metric = Histogram("supportmail_automated_generation_duration", "Duration of the total Execution time of the automated support generation process.")
agenda_rollover_metric = Histogram("agenda_rollover_duration", "Duration of the total Execution time of the agenda rollover process.")

class SupportEngineerManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, username, password, **extra_fields)

class SupportEngineer(AbstractUser):
    objects = SupportEngineerManager()
    username = models.CharField(max_length=255, unique=False)

    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

    def __str__(self):
        return self.first_name

class YEAR_CHOICES(models.TextChoices):
    YEAR_CHOICES = [(str(r), r) for r in range((datetime.datetime.now().year - 5), (datetime.datetime.now().year + 1))]

class EDITION(models.TextChoices):
    JAN = 1, _("January")
    FEB = 2, _("February")
    MAR = 3, _("March")
    APR = 4, _("April")
    MAY = 5, _("May")
    JUN = 6, _("June")
    JUL = 7, _("July")
    AUG = 8, _("August")
    SEP = 9, _("September")
    OCT = 10, _("October")
    NOV = 11, _("November")
    DEC = 12, _("December")

class SupportMail(models.Model):
    edition = models.CharField(max_length=3, choices=EDITION.choices)
    year = models.IntegerField(default=datetime.datetime.now().year)

    class Meta:
        models.UniqueConstraint(fields=["edition", "year"], name="unique_edition")
        db_table = "support_mail_editions"
        ordering = ["-year", "edition"]
        verbose_name = "Support Mail Edition"
        verbose_name_plural = "Support Mail Editions"

    def __str__(self):
        return self.edition - self.year

    @supportmail_generation_metric.time()
    def send_end_of_month_report(self):
        raise NotImplementedError

class Item(models.Model):
    class STATUS(models.TextChoices):
        NEW = "NEW", _("New")
        OPEN = "OPEN", _("Open")
        VISIBILITY = "FYI", _("Visibility Only")
        RESOLVED = "RESOLVED", _("Resolved")
        PUBLISHED = "PUBLISHED", _("Published")
        ACCEPTED = "ACCEPTED", _("Feature Accepted")
        REJECTED = "REJECTED", _("Feature Rejected")
        BACKLOG = "BACKLOG", _("Feature Pending")

    class SECTION(models.TextChoices):
        REVIEW = "REVIEW", _("Ticket Help or Review")
        MONITORING = "MONITOR", _("Ticket Monitoring")
        FOCUS = "FOCUS", _("Client's Need Focus or Attention")
        CALLS = "CALLS", _("Upcoming Client Calls")
        INTERNAL = "INTERNAL", _("Internal Tasks")
        NEEDS = "NEEDS", _("Team, Departmental, Organizational Needs")
        UPDATES = "UPDATES", _("Personal, Social Updates")
        MISC = "MISC", _("Miscellaneous")
        DOCS = "DOCS", _("Documentation Review and Enhancement")
        IFEAT = "IFEAT", _("internal Feature Requests")

    creator = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    date_created = models.DateField(auto_now_add=True)
    date_resolved = models.DateField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True, auto_now=True)
    status = models.CharField(max_length=65535, choices=STATUS.choices, default=STATUS.NEW)
    section = models.CharField(max_length=65535, choices=SECTION.choices)
    title = models.CharField(max_length=65535, null=False, default="")
    link_to_ticket = models.URLField(default="", null=True, blank=True)
    description = MartorField()
    notes = MartorField(null=True, blank=True, default="")
    added_to_supportmail = models.BooleanField(default=False)
    next_task_needed_to_resolve = models.CharField(max_length=65535, null=True, blank=True)
    owner_of_next_task_needed_to_resolve = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT, related_name="item_task_owner", null=True, blank=True)
    added_to_supportmail_on = models.DateField(blank=True, null=True)
    supportmail_edition = models.ForeignKey(SupportMail, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.type_of_incident} - {self.date_occurred}"

    def resolve(self):
        self.status = "RESOLVED"
        self.date_resolved = NOW

    def reopen(self):
        self.status = "OPEN"
        self.date_resolved = None

    def mark_status(self, status):
        if self.section != "IFEAT" and status in ["REJECTED", "ACCEPTED"]:
            raise AgendaItemClassificationError
        self.status = status

    def make_visibility_only(self):
        self.status = "FYI"
        self.section = "MONITOR"

    def add_to_support_mail(self):
        self.added_to_supportmail = True
        self.added_to_supportmail_on = NOW

    def remove_from_supportmail(self):
        self.added_to_supportmail = False
        self.added_to_supportmail_on = None

    def mark_item_published(self, edition_id):
        if not self.added_to_supportmail or self.status == "PUBLISHED":
            raise AgendaItemClassificationError
        self.supportmail_edition = edition_id
        self.status = "PUBLISHED"

    class Meta:
        db_table = "items"
        ordering = ["-date_created"]
        verbose_name = "Agenda Item"
        verbose_name_plural = "Agenda Item"
        constraints = [
            CheckConstraint(check=Q(section__in=["IFEAT"]) & Q(status__in=["NEW", "ACCEPTED", "REJECTED", "BACKLOG"]))
        ]
        indexes = [
            models.Index(fields=["date_created"]),
            models.Index(fields=["date_created", "section", "status"]),
            models.Index(fields=["creator", "section", "status"]),
            models.Index(fields=["added_to_supportmail", "added_to_supportmail_on"]),
            models.Index(fields=["last_modified", "section", "status"]),
            models.Index(fields=["last_modified", "status"]),
            models.Index(fields=["last_modified"])
        ]

class WIN_OOPS(models.Model):
    class TYPE(models.TextChoices):
        WIN = "WIN", _("Win!")
        OOPS = "OOPS", _("Oops")

    date_occurred = models.DateField(auto_now=True)
    type_of_incident = models.CharField(max_length=5, choices=TYPE.choices)
    reported_by = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    clients_involved = models.CharField(max_length=255, null=True)
    description = MartorField()
    added_to_supportmail = models.BooleanField(default=False)

    class Meta:
        db_table = "wins_mistakes"
        ordering = ["-date_occurred"]
        verbose_name = "Win and Mistake"
        verbose_name_plural = "Wins and Mistakes"

class Agenda(models.Model):
    date = models.CharField(primary_key=True, unique=True, default=NOW)
    driver = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT, related_name="driver", null=True)
    notetaker = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT, related_name="notetaker", null=True)

    class Meta:
        db_table = "agendas"
        ordering = ["-date"]
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"
        get_latest_by = "date"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["driver"]),
            models.Index(fields=["notetaker"]),
        ]

    def _select_notetaker(self) -> bool:
        try:
            self.notetaker = Agenda.objects.order_by('-date').first().driver
        except AttributeError:
            logger.warning('No Prior Agenda to Reference. Inserting Dummy Agenda for 01/01/1970')
            dummy_agenda = Agenda.objects.create(
                date="1970-01-01",
                driver=random.choice(list(SupportEngineer.objects.all())),
                notetaker=random.choice(list(SupportEngineer.objects.all()))
            )
            self.notetaker = dummy_agenda.driver

        logger.info(f"Note Taker Selected - {self.notetaker}")
        self.save()
        return True

    def team_selection_randomizer(self, team: QuerySet, selection_type: str) -> SupportEngineer:
        selected_driver = random.choice(team)
        self.driver = selected_driver
        logger.info(f"{selection_type}{self.driver}")
        self.save()
        return selected_driver

    def select_driver(self):
        if self._select_notetaker():
            team = SupportEngineer.objects.exclude(pk=self.notetaker.id) if self.notetaker else SupportEngineer.objects.all()
            self.team_selection_randomizer(team, 'Primary Selection Complete - ')

    def __str__(self):
        return str(self.date)

    def repick_driver(self) -> None:
        logger.info('Initating Manual Driver Reselction')
        former_driver = self.driver
        team = SupportEngineer.objects.exclude(pk=self.notetaker.id).exclude(pk=self.driver.id)
        new_driver = self.team_selection_randomizer(team, 'Reselection Complete - ')
        return {"former_driver": model_to_dict(former_driver, fields=["first_name", "last_name"]), "new_driver": model_to_dict(new_driver, fields=["first_name", "last_name"])}

    @agenda_rollover_metric.time()
    def statusRollOver():
        try:
            logger.info("Starting Item Status Rollover...")
            agenda_qs = Item.objects.filter(status="NEW")
            last_meeting = model_to_dict(Agenda.objects.last())
            last_meeting_date = arrow.get(last_meeting["date"])
            updated_statuses = 0
            for item in agenda_qs:
                item_creation_date = arrow.get(item.date_created)
                if item_creation_date != NOW and item.section not in ["FYI", "IFEAT"]:
                    if last_meeting_date.diff(item_creation_date).in_days() > 1:
                        item.status = "OPEN"
                        item.save()
                        logger.debug("Updated Status on ", item)
                        updated_statuses += 1
                elif item_creation_date != NOW and item.section == "FYI":
                    if last_meeting_date.diff(item_creation_date).in_days() > 1:
                        item.status = "FYI"
                        item.save()
                        logger.debug("Updated Status on ", item)
                        updated_statuses += 1
                elif item_creation_date != NOW and item.section == "IFEAT":
                    if last_meeting_date.diff(item_creation_date).in_days() > 1:
                        item.status = "BACKLOG"
                        item.save()
                        logger.debug("Updated Status on ", item)
                        updated_statuses += 1

            logger.success(f"Completed Status Rollover! {updated_statuses} changed.")
            return True
        except Exception as e:
            logger.error(f"Error when attempting to rollover item status - {e}")
            return False

class Update(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_of_event = models.DateField()
    added_by = models.ForeignKey(SupportEngineer, on_delete=models.CASCADE)
    description = models.CharField(max_length=65535)
    ticket = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.description}({self.added_by})"

    class Meta:
        db_table = "personal_updates"
        ordering = ["-date_created"]
        verbose_name = "Update"
        verbose_name_plural = "Updates"

class ClientCall(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_of_event = models.DateField()
    leading_call = models.ForeignKey(SupportEngineer, on_delete=models.DO_NOTHING)
    topic = models.CharField(max_length=65535)
    client = models.CharField(max_length=65535)
    ticket = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.client} - {self.topic} ({self.date_created})"

    class Meta:
        db_table = "client_calls"
        ordering = ["-date_of_event"]
        verbose_name = "Client Call"
        verbose_name_plural = "Client Calls"
 