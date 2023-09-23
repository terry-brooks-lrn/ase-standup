import datetime
import random

import pendulum
from agenda.managers import SupportEngineerManager
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q, CheckConstraint
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from loguru import logger
import os
from logtail import LogtailHandler

now = pendulum.now(tz="America/Chicago")
now = now.format("YYYY-MM-DD")
PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.remove(0)
logger.add(
    DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG"
)
logger.add(
    PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO"
)
logger.add(
    LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO"
)


class SupportEngineer(AbstractUser):
    objects = SupportEngineerManager()

    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

    def __str__(self):
        return self.first_name


class SupportMail(models.Model):
    class YEAR_CHOICES(models.TextChoices):
        YEAR_CHOICES = []
        for r in range(2023, (datetime.datetime.now().year + 1)):
            YEAR_CHOICES.append((r, r))

    class EDITION(models.TextChoices):
        JAN = 1, _("Janurary")
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
        DEC = 12, _("Decemeber")

    edition = models.CharField(max_length=3, choices=EDITION.choices)
    year = models.IntegerField(default=datetime.datetime.now().year)
    issues = ArrayField(base_field=models.JSONField(), blank=True, null=True)

    class Meta:
        models.UniqueConstraint(fields=["edition", "year"], name="unique_edition")
        db_table = "support_mail_editions"
        ordering = ["-year", "edition"]
        verbose_name = "Support Mail Edition"
        verbose_name_plural = "Support Mail Editions"

    def __str__(self):
        return f"{4} - {self.year}"

    def send_end_of_month_report(self):
        raise NotImplementedError

    # TODO


class Item(models.Model):
    class STATUS(models.TextChoices):
        NEW = "NEW", _("New")
        OPEN = "OPEN", _("Open")
        VISIBILITY = "FYI", _("Visibility Only")
        RESOLVED = "RESOLVED", _("Resolved")

    class SECTION(models.TextChoices):
        REVIEW = "REVIEW", _("Ticket Help or Review")
        MONITORING = "MONITOR", _("Ticket Monitoring")
        FOCUS = "FOCUS", _("Client's Need Focus or Attention")
        CALLS = "CALLS", _("Upcoming Client Calls")
        INTERNAL = "INTERNAL", _("Internal Tasks")
        NEEDS = "NEEDS", _("Team, Departmental, Organizaional Needs")
        UPDATES = "UPDATES", _("Personal, Social Updates")
        MISC = "MISC", _("Miscellaneous")

    creator = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    date_created = models.DateField(auto_now_add=True, null=False)
    date_resolved = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=65535, choices=STATUS.choices, default=STATUS.NEW
    )
    section = models.CharField(max_length=65535, choices=SECTION.choices)
    title = models.CharField(max_length=65535, null=False, default="")
    link_to_ticket = models.URLField(default="", null=True, blank=True)
    description = models.TextField()
    notes = models.TextField(null=True, blank=True)
    next_task_needed_to_resolve = models.CharField(
        max_length=65535, null=True, blank=True
    )
    owner_of_next_task_needed_to_resolve = models.ForeignKey(
        SupportEngineer,
        on_delete=models.PROTECT,
        related_name="item_task_owner",
        null=True,
        blank=True,
    )
    added_to_supportmail = models.BooleanField(default=False)
    date_added_to_supportmail = models.DateField(blank=True, null=True)
    supportmail_edition = models.ForeignKey(
        SupportMail, on_delete=models.PROTECT, blank=True, null=True
    )
    last_modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.date_created} - {self.status}"

    def resolve(self):
        self.status = "RESOLVED"
        self.date_resolved = now

    def reopen(self):
        self.status = "OPEN"
        self.date_resolved = None

    def make_visibility_only(self):
        self.status = "FYI"
        self.section = "MONITOR"

    def add_to_support_mail(self):
        self.added_to_supportmail = True
        self.date_added_to_supportmail = now

    def remove_from_supportmail(self):
        self.added_to_supportmail = False
        self.date_added_to_supportmail = None

    class Meta:
        db_table = "items"
        ordering = ["-date_created"]
        verbose_name = "Agenda Item"
        verbose_name_plural = "Agenda Item"


class WIN_OOPS(models.Model):
    class TYPE(models.TextChoices):
        WIN = "WIN", _("Win!")
        OOPS = "OOPS", _("Oops")

    date_occured = models.DateField(auto_now=True)
    type_of_incident = models.CharField(max_length=5, choices=TYPE.choices)
    reported_by = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    clients_involved = models.CharField(max_length=255, null=True)
    description = models.TextField()
    added_to_supportmail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type_of_incident} - {self.date_occured}"

    def add_to_support_mail(self):
        raise NotImplementedError

    # TODO - Implement Appending Issue to current Month's support mail edition
    class Meta:
        db_table = "wins_mistakes"
        ordering = ["-date_occured"]
        verbose_name = "Win and Mistake"
        verbose_name_plural = "Wins and Mistakes"


class Agenda(models.Model):
    date = models.CharField(primary_key=True, unique=True, default=now)
    driver = models.ForeignKey(
        SupportEngineer, on_delete=models.PROTECT, related_name="driver", null=True
    )
    notetaker = models.ForeignKey(
        SupportEngineer, on_delete=models.PROTECT, related_name="notetaker", null=True
    )

    class Meta:
        db_table = "agendas"
        ordering = ["-date"]
        verbose_name = "Agenda"
        get_latest_by = "date"
        verbose_name_plural = "Agendas"

    def select_driver(self):
        """Class Method to Select Agenda Leaders. Notetaker will always be the driver of the day prior."""
        if self.driver is None:
            most_recent_agenda = Agenda.objects.latest("date")
            CENTRAL_LOGGER.debug(f"Most Recent Agenda:{most_recent_agenda}")
            team = SupportEngineer.objects.all()
            self.driver = random.choice(team)
            last_driver = most_recent_agenda.driver
            CENTRAL_LOGGER.debug(f"Current Driver: {self.driver}")
            CENTRAL_LOGGER.debug(f"Most Recent Driver/Current Scribe[]:{last_driver}")
            if last_driver == self.driver:
                CENTRAL_LOGGER.warning(
                    "Oops...Randomly Selected ther Same Driver as Yesterday. Trying Again."
                )
                self.select_driver()
            CENTRAL_LOGGER.info(f"Driver Selected - {self.driver}")
            self.notetaker = last_driver
            CENTRAL_LOGGER.info(f"Note Taker Selected - {self.notetaker}")
            self.save()
        else:
            CENTRAL_LOGGER.warning(
                "Driver Already Selected - Not Selecting New Driver!"
            )

    def __str__(self):
        return str(self.date)

    @staticmethod
    def statusRollOver():
        """Static Method of the Agenda Class. Thisw utility functuon will mark items that where not created on the same calender day as function is run AND if there a difference of 1 or more days between the item creatioh date and the last datew of the agenda
        Args:
            None
        Rer
        """
        try:
            logger.info("Starting Item Status Rollover...")
            agenda_qs = Item.objects.filter(status="NEW")
            last_meeting = Agenda.objects.latest()
            last_meeting = AgendaSerializer(last_meeting).data
            last_meeting_date = pendulum.parse(last_meeting["date"])
            updated_statuses = 0
            for item in agenda_qs:
                item_creation_date = item.date_created
                item_creation_date = pendulum.datetime(
                    month=item_creation_date.month,
                    day=item_creation_date.day,
                    year=item_creation_date.year,
                )
                if item_creation_date != now:
                    if last_meeting_date.diff(item_creation_date).in_days() > 1:
                        item.status = "OPEN"
                        item.save()
                        logger.debug("Updated Status on ", item)
                        updated_statuses += 1

            logger.success(f"Completed Status Rollover! {updated_statuses} changed.")
            return True
        except Exception as e:
            logger.error(f"Error when attempting to rollover item status - {e}")
            return False
