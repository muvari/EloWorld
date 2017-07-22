from django.db import models
from field_history.tracker import FieldHistoryTracker

# Create your models here.
class League(models.Model):
    name = models.TextField(default='', max_length=20)
    label = models.TextField(default='', max_length=40)

class Player(models.Model):
    name = models.TextField(default='', max_length=20)
    rating = models.IntegerField(default=1500)
    league = models.ForeignKey(League, related_name='players', default=None)
    rating_history = FieldHistoryTracker(['rating'])

class Match(models.Model):
    players = models.ManyToManyField(Player, related_name="matches", through='MatchParticipant')
    time = models.DateTimeField()
    league = models.ForeignKey(League, related_name='matches', default=None)

class MatchParticipant(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    wasRed = models.BooleanField(default=True)
    delta = models.IntegerField(default=0)