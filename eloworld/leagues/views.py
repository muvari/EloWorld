from django.shortcuts import redirect, render
from leagues.models import League, Match, Player, MatchParticipant
import datetime

def home_page(request):
    return render(request, 'home.html')
    
def view_league(request, league_name):
    league_ = League.objects.get(name=league_name)
    return render(request, 'league.html', {'league': league_ })
    
def new_league(request):
    league_ = League.objects.create(name=request.POST['league_name'])
    return redirect(f'/l/{league_.name}/')
    
def add_match(request, league_name):
    redPlayer, rcreated = Player.objects.get_or_create(name=request.POST.get("redname", ""))
    bluePlayer, bcreated = Player.objects.get_or_create(name=request.POST.get("bluename", ""))
    league_ = League.objects.get(name=league_name)
    newMatch = Match.objects.create(time=datetime.datetime.now(), league=league_)
    rmp = MatchParticipant.objects.create(player=redPlayer, match=newMatch, score=request.POST.get("redscore", 0), wasRed=True)
    bmp = MatchParticipant.objects.create(player=bluePlayer, match=newMatch, score=request.POST.get("bluescore", 0), wasRed=False)
    return redirect(f'/l/{league_name}/')