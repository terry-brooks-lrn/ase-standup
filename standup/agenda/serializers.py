from datetime import timedelta

from agenda.models import WIN_OOPS, Agenda, Item, SupportMail, EDITION, YEAR_CHOICES
from django.utils import timezone
from rest_framework import serializers
import arrow
from typing import List, Union, Literal
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            

class WinsMistakesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WIN_OOPS
        fields = "__all__"


class SupportMailSerializers(serializers.ModelSerializer):
    # year = serializers.ChoiceField(choices=YEAR_CHOICES.choices, required=True)
    edition = serializers.ChoiceField(choices=EDITION.choices, required=True)
    issues = serializers.SerializerMethodField(method_name="get_open_unpublished_items")

    # TODO - Implement Logic for All Current Items
    # Pseudo-Code for Method Serializer
    #
    def get_open_unpublished_items(self, obj: Agenda):
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

    """
    `Class for serializing Agenda data.

    Explanation:
    This serializer class handles the serialization of Agenda data, including various items such as review, monitoring, focus, calls, internal, needs, update, misc, and win mistakes.

    Methods:
    - get_filtered_items(obj, section, statuses): Filters and serializes items based on section and statuses.
    - get_review_items(obj: Agenda): Retrieves and filters review items.
    - get_monitoring_items(obj: Agenda): Retrieves and filters monitoring items.
    - get_focus_items(obj: Agenda): Retrieves and filters focus items.
    - get_calls_items(obj: Agenda): Retrieves and filters calls items.
    - get_internal_items(obj: Agenda): Retrieves and filters internal items.
    - get_needs_items(obj: Agenda): Retrieves and filters needs items.
    - get_update_items(obj: Agenda): Retrieves and filters update items.
    - get_misc_items(obj: Agenda): Retrieves and filters miscellaneous items.
    - get_win_mistakes(obj: Agenda): Retrieves and serializes win mistakes data.
    """
    driver = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    notetaker = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    review_items = serializers.SerializerMethodField()
    monitoring_items = serializers.SerializerMethodField()
    focus_items = serializers.SerializerMethodField()
    calls_items = serializers.SerializerMethodField()
    internal_items = serializers.SerializerMethodField()
    # wins_mistakes = serializers.SerializerMethodField(method_name="get_win_mistakes")
    needs_items = serializers.SerializerMethodField()
    update_items = serializers.SerializerMethodField()
    misc_items = serializers.SerializerMethodField()\

    def get_filtered_items(self, obj, section, statuses) -> List[Item]:
        items = Item.objects.filter(section=section, status__in=statuses)
        serialized_items = ItemSerializer(items, many=True)
        return [item for item in serialized_items.data if item["date_created"] < obj.date]

    def get_review_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "REVIEW", ["NEW", "OPEN"])

    def get_monitoring_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "MONITOR", ["NEW", "FYI"])

    def get_focus_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "FOCUS", ["NEW", "OPEN"])

    def get_calls_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "CALLS", ["NEW", "OPEN"])

    def get_internal_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "INTERNAL", ["NEW", "OPEN"])

    def get_needs_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "NEEDS", ["NEW", "OPEN"])

    def get_update_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "UPDATES", ["NEW", "OPEN"])

    def get_misc_items(self, obj: Agenda) -> List[Item]:
        return self.get_filtered_items(obj, "MISC", ["NEW", "OPEN"])

    # def get_win_mistakes(self, obj: Agenda) -> List[WIN_OOPS]:
    #     start_date = arrow.now()
    #     end_date = start_date + timedelta(days=7)
    #     wins_mistakes = WIN_OOPS.objects.filter(
    #         date_occurred__gte=start_date, date_occurred__lte=end_date
    #     )
    #     serialized_items = WinsMistakesSerializer(wins_mistakes, many=True)
    #     return serialized_items.data

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
            # "wins_mistakes",
            "needs_items",
            "update_items",
            "misc_items",
        )
