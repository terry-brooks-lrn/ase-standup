from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import datetime
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _


class SupportEngineer(AbstractUser):
    class Meta:
        db_table = "team_members"
        ordering = ["last_name", "first_name"]
        verbose_name = "Support Engineer"
        verbose_name_plural = "Support Engineers"

class Agenda(models.Model):
    date = models.DateField(primary_key=True, unique=True, auto_now=True)
    driver = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    notetaker = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    sections = models.JSONField(default=dict())
    class Meta:
        db_table = "agendas"
        ordering = ["-date"]
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"

    def select_driver(self):
        team = SupportEngineer.objects.all()
        return random.choice(team)

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
    date_resolved =  models.DateField(auto_now=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS.TextChoices, default=STATUS.NEW)
    section = models.CharField(max_length=10, choices=SECTION.choices)
    title = models.CharField(max_length=255, null=True)
    description = models.TextField()
    notes = models.TextField(null=True)
    added_to_supportmail = models.BooleanField(default=False)

    def solve(self):
        self.status = STATUS.RESOLVED
        return self

    def make_visibility_only(self):
        self.status = STATUS.VISIBILITY
        return self

    def move_to_monitoring(self):
        self.section = SECTION.MONITORING
        return self
    
    def add_to_support_mail(self):
        pass
    # TODO - Implement Appending Issue to current Month's support mail edition 

    class Meta:
        db_table = "items"
        ordering = ["section", "-date_created"]
        verbose_name = "Agenda Item"
        verbose_name_plural = "Agenda Item"

class WIN_OOPS(model.Models):
    class TYPE(models.TextChoices):
        WIN = "WIN", _("Win!")
        OOPS = "OOPS", _("Oops")

    date_occured = models.DateField(auto_now=True)
    type_of_incident = models.CharField(max_length=5, choices=TYPE.choices)
    reported_by = models.ForeignKey(SupportEngineer, on_delete=models.PROTECT)
    clients_involved = models.CharField(max_length=255, null=True)
    description = models.TextField()
    added_to_supportmail = models.BooleanField(default=False)

     def add_to_support_mail(self):
            pass
    # TODO - Implement Appending Issue to current Month's support mail edition 
    class Meta:
        db_table = "wins_mistakes"
        ordering = ["-date_occured"]
        verbose_name = "Win and Mistake"
        verbose_name_plural = "Wins and Mistakes"

class SupportMail(models.Model):
    YEAR_CHOICES = []
    for r in range(2023, (datetime.datetime.now().year+1)):
        YEAR_CHOICES.append((r,r))

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
    edition =  models.CharField(max_length=3, choices=EDITION.choices)
    year = models.IntegerField(_('year'), choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    issues = ArrayField(models.JSONField
    class Meta:
        models.UniqueConstraint(fields=['edition', 'year'], name='unique_edition       db_table = "wins_mistakes"
        ordering = ["-date_occured"]
        verbose_name = "Win and Mistake"
        verbose_name_plural = "Wins and Mistakes"
        
