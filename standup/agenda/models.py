import datetime
import os
import random

import arrow
import arrow
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
from prometheus_client import Histogram

NOW = arrow.now(tz="America/Chicago").format("YYYY-MM-DD")


PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")

supportmail_generation_metric = Histogram("supportmail_automated_generation_duration", "Duration of thr total Execution time of the automated support generation process. ")
agenda_rollover_metric = Histogram("agenda_rollover_duration", "Duratipipon of thr total Execution time of the agenda rollover process. ")
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
        user = self.model(username=username, email=email, password=password, **extra_fields)
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
    username = models.CharField(max_length=255, unique=False)

    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

    def __str__(self):
        return self.first_name


# NOTE - CLASS un-nested from the SupportMail Class to allow for importing and use in the SupportMail Serializer
class YEAR_CHOICES(models.TextChoices):
    YEAR_CHOICES = [
        (str(r), r) for r in range((datetime.datetime.now().year - 5 ), (datetime.datetime.now().year + 1))
    ]

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

    # TODO: Implement Automated Collection Formatting and Distribution of SupportMail  -
    #  Possible packages: 
    #     -  ReportLab for Canvasing and PDFing Content - 
    #     -  Django-SES with AWS SES for Distribution - https://github.com/django-ses/django-ses


class Item(models.Model):
    """
    Model representing an agenda item.

    Explanation:
    This model defines attributes for an agenda item such as creator, dates, status, section, title, links, descriptions, notes, and support mail details. It also includes methods for resolving, reopening, marking as rejected or accepted, setting visibility, managing support mail, and publishing items.

    Methods:
    - resolve(): Resolves the agenda item.
    - reopen(): Reopens the agenda item.
    - mark_rejected(): Marks the agenda item as rejected.
    - mark_accepted(): Marks the agenda item as accepted.
    - make_visibility_only(): Sets the visibility of the agenda item to only monitoring.
    - add_to_support_mail(): Adds the edition to the support mail.
    - remove_from_supportmail(): Removes the item from the support mail.
    - mark_item_published(edition_id): Marks the item as published for a specific support mail edition.

    Raises:
    - AgendaItemClassificationError: If the section is not "IFEAT" for mark_rejected() or mark_accepted() methods, or if conditions are not met for mark_item_published().

    Attributes:
    - creator: ForeignKey to SupportEngineer.
    - date_created: DateField for creation date.
    - date_resolved: DateField for resolution date.
    - last_modified: DateTimeField for last modification.
    - status: CharField for status.
    - section: CharField for section.
    - title: CharField for title.
    - link_to_ticket: URLField for ticket link.
    - description: MartorField for description.
    - notes: MartorField for additional notes.
    - added_to_supportmail: BooleanField for support mail addition.
    - next_task_needed_to_resolve: CharField for next task.
    - owner_of_next_task_needed_to_resolve: ForeignKey to SupportEngineer.
    - added_to_supportmail_on: DateField for support mail addition date.
    - supportmail_edition: ForeignKey to SupportMail.
    """

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
        """
        Class defining choices for different sections.

        Explanation:
        This class defines choices for various sections such as review, monitoring, focus, calls, internal tasks, needs, updates, miscellaneous tasks, documentation review, and internal feature requests.

        Attributes:
        - REVIEW: Ticket Help or Review
        - MONITORING: Ticket Monitoring
        - FOCUS: Client's Need Focus or Attention
        - CALLS: Upcoming Client Calls
        - INTERNAL: Internal Tasks
        - NEEDS: Team, Departmental, Organizational Needs
        - UPDATES: Personal, Social Updates
        - MISC: Miscellaneous
        - DOCS: Documentation Review and Enhancement
        - IFEAT: Internal Feature Requests
        """
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
        return f"{self.type_of_incident} - {self.date_occurred}"

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
        """Sets the visibility of the agenda item to only monitoring only.

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
        self.supportmail_edition = edition_id
        self.status = "PUBLISHED"

    class Meta:
        db_table = "items"
        ordering = ["-date_created"]
        verbose_name = "Agenda Item"
        verbose_name_plural = "Agenda Item"
        CheckConstraint(
            check=Q(section__in=["IFEAT"])
            & Q(status__in=["NEW", "ACCEPTED", "REJECTED", "BACKLOG"]),
            name="age_gte_18",
        )
        indexes = [
            models.Index(fields=["date_created"]),
            models.Index(fields=["date_created", "section", "status"]),
            models.Index(fields=["creator", "section", "status"]),
            models.Index(fields=["added_to_supportmail","added_to_supportmail_on"]),        
            models.Index(fields=["last_modified","section", "status"]),        
            models.Index(fields=["last_modified", "status"]),        
            models.Index(fields=["last_modified"])
            ]


class WIN_OOPS(models.Model):
    """
    This model represents an entry for either a win or a mistake, storing the date it occurred, the type of incident (win or oops), the support engineer who reported it, clients involved, a description, and whether it was added to the support mail. It also defines the database table name, ordering, and verbose names.

    Attributes:
        - date_occurred: The date the incident occurred.
        - type_of_incident: The type of incident (win or oops).
        - reported_by: The support engineer who reported the incident.
        - clients_involved: Names of clients involved (optional).
        - description: Description of the incident.
        - added_to_supportmail: Indicates if the incident was added to the support mail.

    """

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
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["driver"]),
            models.Index(fields=["notetaker"]),
        ]

    def _select_notetaker(self):
        """Selects the notetaker for the current agenda.

        This function retrieves the most recent agenda before the current date and assigns its driver as the notetaker for the current agenda. It also logs the selection of the notetaker and saves the changes.

        Args:
            self: The instance.

        Returns:
            None.

        NOTE: Method is never called directly, It is invoked whn the '.select_driver()' method.
        """

        self.notetaker = Agenda.objects.order_by('-date').first().driver
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
    
    @agenda_rollover_metric.time()
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
            last_meeting_date = arrow.get(last_meeting["date"])
            updated_statuses = 0
            for item in agenda_qs:
                item_creation_date = arrow.get(item.date_created)
                # item_creation_date = arrow.get(
                #     month=item_creation_date.month,
                #     day=item_creation_date.day,
                #     year=item_creation_date.year,
                # )
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

    def __str__(self):
        return f"{self.description}({self.added_by})"
    class Meta:
        db_table = "personal_updates"
        ordering = ["-date_created"]
        verbose_name = "Update"
        verbose_name_plural = "Updates"

class ClientCalls(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_of_event = models.DateField()
    leading_call = models.ForeignKey(SupportEngineer, on_delete=models.DO_NOTHING)
    topic = models.CharField(max_length=65535)
    client = models.CharField(max_length=65535)

    def __str__(self):
        return f"{self.client} - {self.topic} ({self.date_created})"
    class Meta:
        db_table = "client_calls"
        ordering = ["-date_of_event"]
        verbose_name = "Client Call"
        verbose_name_plural = "Client Calls"