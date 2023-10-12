from datetime import timedelta
from agenda.models import WIN_OOPS, Agenda, Item, SupportMail, EDITION, YEAR_CHOICES
from django.utils import timezone
from rest_framework import serializers


class ItemSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Item.STATUS.choices, read_only=True)

    class Meta:
        model = Item
        fields = (
            "creator",
            "date_created",
            "section",
            "title",
            "link_to_ticket",
            "description",
            "notes",
            "next_task_needed_to_resolve",
            "owner_of_next_task_needed_to_resolve",
            "added_to_supportmail",
        )


class WinsMistakesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WIN_OOPS
        fields = "__all__"


class SupportMailSerializer(serializers.ModelSerializer):
    year = serializers.ChoiceField(choices=YEAR_CHOICES.choices, required=True)
    edition = serializers.ChoiceField(choices=EDITION.choices, required=True)
    issues = serializers.SerializerMethodField(method_name="get_open_unpublished_items")

    # TODO - Implement Logic for All Current Items
    # Pseudo-Code for Method Seralizer
    #
    def get_open_unpublished_items(self, obj):
        current_issued = Item.objects.filter(
            added_to_supportmail=True,
        )

    class Meta:
        model = SupportMail
        fields = (
            "year",
            "edition",
            "issues",
        )


class AgendaSerializer(serializers.ModelSerializer):
    driver = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    notetaker = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    review_items = serializers.SerializerMethodField()
    monitoring_items = serializers.SerializerMethodField()
    focus_items = serializers.SerializerMethodField()
    calls_items = serializers.SerializerMethodField()
    internal_items = serializers.SerializerMethodField()
    wins_mistakes = serializers.SerializerMethodField(method_name="get_win_mistakes")
    needs_items = serializers.SerializerMethodField()
    update_items = serializers.SerializerMethodField()
    misc_items = serializers.SerializerMethodField()

    def get_review_items(self, obj):
        """Get review items.

        Args:
            obj: The object to compare the date with.

        Returns:
            A list of valid review items that have a date_created earlier than obj.date.
        """

        review_items = Item.objects.filter(section="REVIEW", status__in=["NEW", "OPEN"])
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_monitoring_items(self, obj):
        review_items = Item.objects.filter(section="MONITOR", status__in=["NEW", "FYI"])
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_focus_items(self, obj):
        review_items = Item.objects.filter(section="FOCUS", status__in=["NEW", "OPEN"])
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_calls_items(self, obj):
        review_items = Item.objects.filter(section="CALLS", status__in=["NEW", "OPEN"])
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_internal_items(self, obj):
        review_items = Item.objects.filter(
            section="INTERNAL", status__in=["NEW", "OPEN"]
        )
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_needs_items(self, obj):
        review_items = Item.objects.filter(section="NEEDS", status__in=["NEW", "OPEN"])
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_update_items(self, obj):
        review_items = Item.objects.filter(
            section="UPDATES", status__in=["NEW", "OPEN"]
        )
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_misc_items(self, obj):
        review_items = Item.objects.filter(section="MISC", status__in=["NEW", "OPEN"])
        serialized_review_items = ItemSerializer(review_items, many=True)
        valid_items = list()
        for item in serialized_review_items.data:
            if item["date_created"] < obj.date:
                valid_items.append(item)
        return valid_items

    def get_win_mistakes(self, obj):
        startdate = timezone.now()
        enddate = startdate + timedelta(days=7)

        wins_mistakes = WIN_OOPS.objects.filter(
            date_occured__gte=startdate, date_occured__lte=enddate

        )
        serialized_items = WinsMistakesSerializer(wins_mistakes, many=True)
        return serialized_items.data

    def get_win_mistakes(self, obj):
        startdate = timezone.now()
        enddate = startdate + timedelta(days=7)

        wins_mistakes = WIN_OOPS.objects.filter(
            date_occured__gte=startdate, date_occured__lte=enddate
        )
        serialized_items = WinsMistakesSerializer(wins_mistakes, many=True)
        return serialized_items.data

    class Meta:
        model = Agenda
        fields = (
            "date",
            "driver",
            "notetaker",
            "review_items",
            "monitoring_items",
            "focus_items",
            "calls_items",
            "internal_items",
            "wins_mistakes",
            "needs_items",
            "update_items",
            "misc_items",
        )
