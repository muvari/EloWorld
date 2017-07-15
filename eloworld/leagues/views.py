from django.shortcuts import redirect, render
from leagues.models import League, Match, Player, MatchParticipant
import datetime

def home_page(request):
    return render(request, 'home.html')
    
def view_league(request, league_name):
    league_ = League.objects.get(name=league_name)

    player_list = []
    players = Player.objects.order_by('rating')
    for p in players:
        total_points = 0
        opponent_points = 0
        diff = 0.0
        for m in p.matches.all():
            if p.name == m.matchparticipant_set.all()[0].player.name:
                total_points += m.matchparticipant_set.all()[0].score
                opponent_points += m.matchparticipant_set.all()[1].score
            else:
                total_points += m.matchparticipant_set.all()[1].score
                opponent_points += m.matchparticipant_set.all()[0].score

        diff = (total_points - opponent_points) / p.matches.count()

        p_list = {'name': p.name, 'matches': p.matches.count(), 'diff': diff, 'rating': p.rating}
        player_list.append(p_list)


    return render(request, 'league.html', {'league': league_, 'player_list': player_list })
    
def new_league(request):
    league_, created = League.objects.get_or_create(name=request.POST['league_name'])
    return redirect(f'/l/{league_.name}/')
    
def add_match(request, league_name):
    league_ = League.objects.get(name=league_name)
    redPlayer, rcreated = Player.objects.get_or_create(name=request.POST.get("redname", ""), league=league_)
    bluePlayer, bcreated = Player.objects.get_or_create(name=request.POST.get("bluename", ""), league=league_)
    newMatch = Match.objects.create(time=datetime.datetime.now(), league=league_)
    rmp = MatchParticipant.objects.create(player=redPlayer, match=newMatch, score=request.POST.get("redscore", 0), wasRed=True)
    bmp = MatchParticipant.objects.create(player=bluePlayer, match=newMatch, score=request.POST.get("bluescore", 0), wasRed=False)
    return redirect(f'/l/{league_name}/')