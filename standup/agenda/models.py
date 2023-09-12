import datetime
import random

import pendulum
from agenda.managers import SupportEngineerManager
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from loguru import logger

now = pendulum.now(tz="America/Chicago")
now = now.format("YYYY-MM-DD")


class SupportEngineer(AbstractUser):
    objects = SupportEngineerManager()

    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

    def __str__(self):
        return self.first_name


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
    date_created = models.DateField(auto_now=True)
    date_resolved = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=65535, choices=STATUS.choices, default=STATUS.NEW)
    section = models.CharField(max_length=65535, choices=SECTION.choices)
    title = models.CharField(max_length=65535, null=False, default="")
    link_to_ticket = models.URLField(default="", null=True)
    description = models.TextField()
    notes = models.TextField(null=True)
    added_to_supportmail = models.BooleanField(default=False)

    def solve(self):
        self.status = STATUS.RESOLVED
        return self

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

    def remove_from_supportmail(self):
        self.added_to_supportmail = False

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


class SupportMail(models.Model):
    class YEAR_CHOICES(models.TextChoices):
        YEAR_CHOICES = []
        for r in range(2023, (datetime.datetime.now().year + 1)):
            YEAR_CHOICES.append((r, r))

    class EDITION(models.TextChoices):
        JAN = "JAN", _("Janurary")
        FEB = "FEB", _("February")
        MAR = "MAR", _("March")
        APR = "APR", _("April")
        MAY = "MAY", _("May")
        JUN = "JUN", _("June")
        JUL = "JUL", _("July")
        AUG = "AUG", _("August")
        SEP = "SEP", _("September")
        OCT = "OCT", _("October")
        NOV = "NOV", _("November")
        DEC = "DEC", _("Decemeber")

    edition = models.CharField(max_length=3, choices=EDITION.choices)
    year = models.IntegerField(default=datetime.datetime.now().year)
    issues = ArrayField(
        base_field=models.JSONField(),
        blank=True,
    )

    class Meta:
        models.UniqueConstraint(fields=["edition", "year"], name="unique_edition")
        db_table = "support_mail_editions"
        ordering = ["-year", "edition"]
        verbose_name = "Support Mail Edition"
        verbose_name_plural = "Support Mail Editions"

    def __str__(self):
        return self.edition - self.year

    def send_end_of_month_report(self):
        raise NotImplementedError

    # TODO


class Agenda(models.Model):
    date = models.CharField(primary_key=True, unique=True, default=now)
    driver = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT, related_name="driver", null=True)
    notetaker = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT, related_name="notetaker", null=True)

    class Meta:
        db_table = "agendas"
        ordering = ["-date"]
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"

    def select_driver(self):
        """Class Method to Select Agenda Leaders. Notetaker will always be the driver of the day prior."""
        if self.driver is None:
            most_recent_agenda = Agenda.objects.latest("date")
            logger.debug(f"Most Recent Agenda:{most_recent_agenda}")
            team = SupportEngineer.objects.all()
            self.driver = random.choice(team)
            last_driver = most_recent_agenda.driver
            logger.debug(f"Current Driver: {self.driver}")
            logger.debug(f"Most Recent Driver/Current Scribe[]:{last_driver}")
            if last_driver == self.driver:
                logger.warning("Oops...Randomly Selected ther Same Driver as Yesterday. Trying Again.")
                self.select_driver()
            logger.info(f"Driver Selected - {self.driver}")
            self.notetaker = last_driver
            logger.info(f"Note Taker Selected - {self.notetaker}")
            self.save()
        else:
            logger.warning("Driver Already Selected - Not Selecting New Driver!")

    def __str__(self):
        return str(self.date)
