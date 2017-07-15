from django.contrib import admin
from leagues.models import League, Match, Player, MatchParticipant
# Register your models here.

admin.site.register(League)
admin.site.register(Match)
admin.site.register(Player)
admin.site.register(MatchParticipant)