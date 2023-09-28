from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import datetime
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from loguru import logger
from agenda.managers import SupportEngineerManager
import pendulum
from logtail import LogtailHandler
import os
from django.conf import settings

# SECTION - Important note - This insatation of the Current date and time is used by other modules Deletion or altering this instance is not possible
now = pendulum.now(tz="America/Chicago")
now = now.format("YYYY-MM-DD")


PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")


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
    last_modified = models.DateTimeField(blank=True, null=True, auto_now=True)
    status = models.CharField(
        max_length=65535, choices=STATUS.choices, default=STATUS.NEW
    )
    section = models.CharField(max_length=65535, choices=SECTION.choices)
    title = models.CharField(max_length=65535, null=False, default="")
    link_to_ticket = models.URLField(default="", null=True, blank=True)
    description = models.TextField()
    notes = models.TextField(null=True, blank=True)
    added_to_supportmail = models.BooleanField(default=False)
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
    # date_added_to_supportmail = models.DateField(blank=True, ÷…ænull=True)
    supportmail_edition = models.ForeignKey(
        SupportMail, on_delete=models.PROTECT, blank=True, null=True
    )

    def __str__(self):
        return f"{self.type_of_incident} - {self.date_occured}"

    def resolve(self):
        """Resolves the current agenda item.

        This method sets the status of the issue to "RESOLVED" and updates the date_resolved attribute with the current date and time.

        Args:
            self: The instance.

        Returns:
            None.
        """

        self.status = "RESOLVED"
        self.date_resolved = now

    def reopen(self):
        """Reopens the agenda item.

        This method sets the status of the issue to "OPEN" and clears the resolved date.

        Args:
            self: The instance.

        Returns:
            None.
        """

        self.status = "OPEN"
        self.date_resolved = None

    def make_visibility_only(self):
        """Sets the visibility of the agenda item to only monioring only.

        This method sets the `status` attribute of the object to "FYI" and the `section` attribute to "MONITOR". This ensures that the object is only visible to users with the FYI and MONITOR access levels.

        Args:
            self: The instance.

        Returns:
            None.
        """

        self.status = "FYI"
        self.section = "MONITOR"

    def add_to_support_mail(self):
        """Adds the  edition to the support mail.

        This method sets the `added_to_supportmail` attribute of the  instance to True and assigns the current date and time to the `date_added_to_supportmail` attribute.

        Args:
            self: The instance.

        Returns:
            None.
        """

        self.added_to_supportmail = True
        self.date_added_to_supportmail = now

    def remove_from_supportmail(self):
        """Removes the current edition from the support mail.

        This function sets the 'added_to_supportmail' attribute to False and the 'date_added_to_supportmail' attribute to None.

        Args:
            self: The  instance of the class.

        Returns:
            None
        """

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
        verbose_name_plural = "Agendas"

    def _select_notetaker(self):
        """Selects the notetaker for the current agenda.

        This function retrieves the most recent agenda before the current date and assigns its driver as the notetaker for the current agenda. It also logs the selection of the notetaker and saves the changes.

        Args:
            self: The instance.

        Returns:
            None.

        NOTE: Method is never called direcly, It is involked whn the '.select_driver()' method.
        """

        # most_recent_date = pendulum.parse(self.date).subtract(days=1).to_date_string()
        most_recent_agenda = Agenda.objects.latest("date")
        self.notetaker = most_recent_agenda.driver
        logger.info(f"Note Taker Selected - {self.notetaker}")
        self.save()

    def select_driver(self):
        self._select_notetaker()
        team = SupportEngineer.objects.all()
        self.driver = random.choice(team)
        logger.info(f"Driver Selected - {self.driver}")
        self.save()

    def __str__(self):
        return str(self.date)


@staticmethod
def statusRollOver():
    """Static Method of the Agenda Class. This utility function will mark items that were not created on the same calendar day as the function is run AND if there is a difference of 1 or more days between the item creation date and the last date of the agenda.

    Args:
        None

    Returns:
        bool: True if the status rollover is completed successfully, False otherwise.
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
