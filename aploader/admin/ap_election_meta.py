from django import forms
from django.contrib import admin

from election.models import Election


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}: {} {} {}".format(
            obj.election_day.date,
            obj.race.label,
            obj.party.label if obj.party else "",
            obj.election_type.label,
        )


class APElectionMetaAdminForm(forms.ModelForm):
    election = CustomModelChoiceField(
        queryset=Election.objects.all().order_by(
            "election_day__date", "division__label", "party"
        )
    )


class APElectionMetaAdmin(admin.ModelAdmin):
    form = APElectionMetaAdminForm
    list_display = (
        "get_office",
        "get_date",
        "get_type",
        "get_party",
        "get_special",
    )
    ordering = (
        "-election__election_day__date",
        "election__division__label",
        "election__party",
    )
    search_fields = (
        "election__race__label",
        "election__election_day__date",
        "election__election_day__slug",
    )
    list_filter = (
        "election__election_day__date",
        "election__race__special",
        "election__election_type__label",
    )

    fieldsets = (
        ("Identification", {"fields": ("ap_election_id",)}),
        ("Relationships", {"fields": ("election", "ballot_measure")}),
        (
            "Overrides",
            {
                "fields": (
                    "called",
                    "tabulated",
                    "override_ap_call",
                    "override_ap_votes",
                )
            },
        ),
        (
            "Precincts",
            {
                "fields": (
                    "precincts_reporting",
                    "precincts_total",
                    "precincts_reporting_pct",
                )
            },
        ),
    )

    def get_office(self, obj):
        return obj.election.race.office.label

    def get_date(self, obj):
        return obj.election.election_day.date

    def get_party(self, obj):
        if obj.election.party:
            return obj.election.party.label
        else:
            return None

    def get_type(self, obj):
        return obj.election.election_type.label

    def get_special(self, obj):
        return obj.election.race.special

    get_office.short_description = "Office"
    get_date.short_description = "Election date"
    get_party.short_description = "Primary party"
    get_type.short_description = "Election type"
    get_special.short_description = "Special"
