import datetime
import os
import random

import pendulum
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from logtail import LogtailHandler
from martor.models import MartorField
from loguru import logger
from django.db.models import Q
from django.db.models.constraints import CheckConstraint
from agenda.errors import AgendaItemClassificationError
from django.contrib.auth.base_user import BaseUserManager
from agenda.errors import DuplicateUsernameError

# SECTION - Important note - This insatation of the Current date and time is used by other modules Deletion or altering this instance is not possible
NOW = pendulum.now(tz="America/Chicago")
NOW = NOW.format("YYYY-MM-DD")


PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")


class SupportEngineerManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
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

    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

    def __str__(self):
        return self.first_name


# NOTE - CLASS un-nested from the SupportMail Class to allow for importimg and use in the SupportMail Serializer
class YEAR_CHOICES(models.TextChoices):
    YEAR_CHOICES = []
    for r in range(2023, (datetime.datetime.now().year + 1)):
        YEAR_CHOICES.append((r, r))


# NOTE - CLASS un-nested from the SupportMail Class to allow for importimg and use in the SupportMail Serializer \
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

    def send_end_of_month_report(self):
        raise NotImplementedError

    # TODO


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
        NEEDS = "NEEDS", _("Team, Departmental, Organizaional Needs")
        UPDATES = "UPDATES", _("Personal, Social Updates")
        MISC = "MISC", _("Miscellaneous")
        DOCS = "DOCS", _("Documentation Review and Enhancement")
        IFEAT = "IFEAT", _("internal Feature Requests")

    creator = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    date_created = models.DateField(auto_now_add=True)
    date_resolved = models.DateField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True, auto_now=True)
    status = models.CharField(
        max_length=65535, choices=STATUS.choices, default=STATUS.NEW
    )
    section = models.CharField(max_length=65535, choices=SECTION.choices)
    title = models.CharField(max_length=65535, null=False, default="")
    link_to_ticket = models.URLField(default="", null=True, blank=True)
    description = MartorField()
    notes = MartorField(null=True, blank=True, default="")
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
    added_to_supportmail_on = models.DateField(blank=True, null=True)
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
        self.date_resolved = NOW

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

    def mark_rejected(self):
        """Marks the agenda item as rejected.

        Raises:
            AgendaItemClassificationError: If the section of the agenda item is not "IFEAT".
        """

        if self.section != "IFEAT":
            raise AgendaItemClassificationError
        else:
            self.status = "REJECTED"

    def mark_accepted(self):
        """Marks the agenda item as accepted.

        Raises:
            AgendaItemClassificationError: If the section of the agenda item is not "IFEAT".
        """

        if self.section != "IFEAT":
            raise AgendaItemClassificationError
        else:
            self.status = "ACCEPTED"

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
        self.added_to_supportmail_on = NOW

    def remove_from_supportmail(self):
        """Removes the current edition from the support mail.

        This function sets the 'added_to_supportmail' attribute to False and the 'date_added_to_supportmail' attribute to None.

        Args:
            self: The  instance of the class.

        Returns:
            None.
        """

        self.added_to_supportmail = False
        self.added_to_supportmail_on = None

    def mark_item_published(self, edition_id):
        """Marks an item that has been added to support as published.

        Args:
            edition_id (int): The PK of the SupportMail edition that this item is to be published.

        Raises:
            AgendaItemClassificationError: If `add_to_support_mail` is `False` or the item has already been published.

        Returns:
            None.
        """

        if self.add_to_support_mail == False or self.status == "PUBLISHED":
            raise AgendaItemClassificationError
        else:
            self.supportmail_edition = edition_id
            self.status = "PUBLISHED"

    class Meta:
        db_table = "items"
        ordering = ["-date_created"]
        verbose_name = "Agenda Item"
        verbose_name_plural = "Agenda Item"
        CheckConstraint(
            check=Q(section__in=["IFEAT"])
            & Q(status__in=["NEW", "ACCETED", "REJECTED", "BACKLOG"]),
            name="age_gte_18",
        )


class WIN_OOPS(models.Model):
    class TYPE(models.TextChoices):
        WIN = "WIN", _("Win!")
        OOPS = "OOPS", _("Oops")

    date_occured = models.DateField(auto_now=True)
    type_of_incident = models.CharField(max_length=5, choices=TYPE.choices)
    reported_by = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    clients_involved = models.CharField(max_length=255, null=True)
    description = MartorField()
    added_to_supportmail = models.BooleanField(default=False)

    class Meta:
        db_table = "wins_mistakes"
        ordering = ["-date_occured"]
        verbose_name = "Win and Mistake"
        verbose_name_plural = "Wins and Mistakes"


class Agenda(models.Model):
    date = models.CharField(primary_key=True, unique=True, default=NOW)
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
        get_latest_by = ["date"]


    def _select_notetaker(self):
        """Selects the notetaker for the current agenda.

        This function retrieves the most recent agenda before the current date and assigns its driver as the notetaker for the current agenda. It also logs the selection of the notetaker and saves the changes.

        Args:
            self: The instance.

        Returns:
            None.

        NOTE: Method is never called directly, It is invoked whn the '.select_driver()' method.
        """

        most_recent_agenda = Agenda.objects.last()
        self.notetaker = most_recent_agenda.driver
        logger.info(f"Note Taker Selected - {self.notetaker}")
        self.save()

    def select_driver(self):
        """Selects a driver from the team of support engineers.

        This method first selects a notetaker using the `_select_notetaker` method. Then, it retrieves all support engineers from the database and randomly selects one as the driver. If the selected driver is the same as the notetaker, the method recursively calls itself until a different driver is selected. Finally, it logs the selected driver and saves the changes.

        Returns:
            None
        """

        self._select_notetaker()
        team = SupportEngineer.objects.all()
        self.driver = random.choice(team)
        if self.driver == self.notetaker:
            self.select_driver()
        else:
            logger.info(f"Driver Selected - {self.driver}")
            self.save()

    def __str__(self):
        return str(self.date)

    def statusRollOver():
        """Static Method of the Agenda Class. This utility function will mark items that were not created on the same calendar day as the function is run AND if there is a difference of 1 or more days between the item creation date and the last date of the agenda.

        Args:
            None

        Returns:
            bool: True if the status rollover is completed successfully, returns False and logs error to error handlers.
        """
        try:
            logger.info("Starting Ite Status Rollover...")
            agenda_qs = Item.objects.filter(status="NEW")
            last_meeting = model_to_dict(Agenda.objects.last())
            last_meeting_date = pendulum.parse(last_meeting["date"])
            updated_statuses = 0
            for item in agenda_qs:
                item_creation_date = item.date_created
                item_creation_date = pendulum.datetime(
                    month=item_creation_date.month,
                    day=item_creation_date.day,
                    year=item_creation_date.year,
                )
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
