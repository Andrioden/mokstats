from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import Match, Place, Player, PlayerResult


class ResultInlineFormset(BaseInlineFormSet):
    def clean(self) -> None:
        forms = [form for form in self.forms if form.cleaned_data]

        player_count = len(forms)
        if player_count < 3:
            raise ValidationError("Må minst vær 3 spillere")

        spades_total = sum(form.cleaned_data.get("sum_spades", 0) for form in forms)
        queens_total = sum(form.cleaned_data.get("sum_queens", 0) for form in forms)
        if any(f for f in forms if f.cleaned_data.get("sum_queens", 0) % 4 != 0):
            raise ValidationError("Ugyldig dameverdi, må være multiplikasjon av 4")
        pass_total = sum(form.cleaned_data.get("sum_pass", 0) for form in forms)
        grand_total = sum(form.cleaned_data.get("sum_grand", 0) for form in forms)
        trumph_total = sum(form.cleaned_data.get("sum_trumph", 0) for form in forms)
        players_with_zero_solitaire_cards = len([f for f in forms if f.cleaned_data.get("sum_solitaire_cards", 0) == 0])

        spades_in_play = 12 if player_count in [6, 8, 9] else 13
        cards_per_player = 52 // player_count

        self.validate_eq(spades_total, spades_in_play, "Ugyldig Spa-poeng gitt, %s totalt nå, %s krevd")
        self.validate_eq(queens_total, 16, "Ugyldig Dame-poeng gitt, %s totalt nå, %s krevd")
        self.validate_eq(players_with_zero_solitaire_cards, 1, "%s spillere med 0 kort igjen i Kabal, %s krevd")
        self.validate_eq(pass_total, cards_per_player, "Ugyldig Pass-poeng gitt, %s totalt nå, %s krevd")
        self.validate_eq(grand_total, cards_per_player, "Ugyldig Grand-poeng gitt, %s totalt nå, %s krevd")
        self.validate_eq(trumph_total, cards_per_player, "Ugyldig Trumf-poeng gitt, %s totalt nå, %s krevd")

    @classmethod
    def validate_eq(cls, a: int, b: int, message: str) -> None:
        if a != b:
            raise ValidationError(message % (a, b))


class ResultInline(admin.TabularInline):
    exclude = ("rating",)
    readonly_fields = ["total"]
    model = PlayerResult
    formset = ResultInlineFormset
    extra = 0
    min_num = 3


class MatchAdmin(admin.ModelAdmin):
    inlines = [ResultInline]

    class Media:
        js = ("https://code.jquery.com/jquery-1.8.2.min.js", "admin_custom.js")
        css = {"all": ("admin_custom.css",)}


class ConfigurationAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("admin_custom.css",)}


admin.site.register(Player)
admin.site.register(Place)
admin.site.register(Match, MatchAdmin)
