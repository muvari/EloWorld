from django.db import models

# Create your models here.
class League(models.Model):
    name = models.TextField(default='')

class Player(models.Model):
    name = models.TextField(default='')
    rating = models.IntegerField(default=1500)

class Match(models.Model):
    players = models.ManyToManyField(Player, through='MatchParticipant')
    time = models.DateTimeField()
    league = models.ForeignKey(League, related_name='matches', default=None)

class MatchParticipant(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    wasRed = models.BooleanField(default=True)