from django.shortcuts import redirect, render
from leagues.models import League, Match, Player, MatchParticipant
from elo import elo
import datetime, math

def home_page(request):
    return render(request, 'home.html')
    
def view_league(request, league_name):
    league_ = League.objects.get(name=league_name)

    origin = datetime.date(2017, 7, 7)
    fDoW = datetime.date.today() - datetime.timedelta(days=datetime.date.today().isoweekday() % 7)

    player_list = []
    players = league_.players.order_by('-rating')
    for p in players:
        history = list(p.get_rating_history().filter(date_created__range=[origin, fDoW]).order_by('date_created'))
        if len(history) > 0:
            last = p.rating - history[len(history) - 1].field_value 
        else:
            last = p.rating - 1500

        lastStr = diffStr = str(round(last, 0))
        if last > 0:
            lastStr = "+" + lastStr

        p_list = {'name': p.name, 'last': lastStr, 'rating': p.rating}
        player_list.append(p_list)

    playernames = list(players.values_list('name', flat=True))
    past_20_matches = league_.matches.order_by('-time')[:20]
    return render(request, 'league.html', {'league': league_, 
                                            'player_list': player_list, 
                                            'playernames' : playernames, 
                                            'matches' : past_20_matches })
    
def new_league(request):
    lName = request.POST['league_name'].lower()
    league_, created = League.objects.get_or_create(name=lName)
    if created==True:
        league_.label = request.POST['league_label']
    league_.save()
    return redirect(f'/l/{league_.name}/')
    
def add_match(request, league_name):
    league_ = League.objects.get(name=league_name)
    redScore = int(request.POST.get("redscore", 0))
    blueScore = int(request.POST.get("bluescore", 0))
    redPlayer, rcreated = Player.objects.get_or_create(name=request.POST.get("redname", ""), league=league_)
    bluePlayer, bcreated = Player.objects.get_or_create(name=request.POST.get("bluename", ""), league=league_)
    newMatch = Match.objects.create(time=datetime.datetime.now(), league=league_)
    rmp = MatchParticipant.objects.create(player=redPlayer, match=newMatch, score=redScore, wasRed=True)
    bmp = MatchParticipant.objects.create(player=bluePlayer, match=newMatch, score=blueScore, wasRed=False)

    redRating = redPlayer.rating
    blueRating = bluePlayer.rating

    redExp = elo.expected(redRating, blueRating)
    blueExp = elo.expected(blueRating, redRating)

    if redScore > blueScore:
        winRating = redRating
        loseRating = blueRating
    else:
        winRating = blueRating
        loseRating = redRating

    if redScore + blueScore > 18:
        diff = 1
    else:
        diff = abs(redScore - blueScore)

    km = elo.k_mult(elo.adjustedDiff(diff), winRating, loseRating)

    newRedElo = elo.elo(redRating, redExp, redScore > blueScore, km)
    newBlueElo = elo.elo(blueRating, blueExp, blueScore > redScore, km)
    rmp.delta = newRedElo - redRating
    bmp.delta = newBlueElo - blueRating

    redPlayer.rating = newRedElo
    bluePlayer.rating = newBlueElo
    redPlayer.save()
    bluePlayer.save()
    rmp.save()
    bmp.save()
    
    return redirect(f'/l/{league_name}/')