from django.shortcuts import redirect, render
from leagues.models import League, Match, Player, MatchParticipant
import datetime, math

def home_page(request):
    return render(request, 'home.html')
    
def view_league(request, league_name):
    league_ = League.objects.get(name=league_name)

    player_list = []
    players = league_.players.order_by('-rating')
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
        diffStr = str(round(diff, 1))
        if diff > 0:
            diffStr = '+' + diffStr

        p_list = {'name': p.name, 'matches': p.matches.count(), 'diff': diffStr, 'rating': p.rating}
        player_list.append(p_list)

    playernames = list(players.values_list('name', flat=True))
    return render(request, 'league.html', {'league': league_, 'player_list': player_list, 'playernames' : playernames })
    
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

    redExp = expected(redRating, blueRating)
    blueExp = expected(blueRating, redRating)

    if redScore > blueScore:
        winRating = redRating
        loseRating = blueRating
    else:
        winRating = redRating
        loseRating = blueRating

    if redScore + blueScore > 18:
        diff = 1
    else:
        diff = abs(redScore - blueScore)

    km = k_mult(min(6, diff), winRating, loseRating)

    newRedElo = elo(redRating, redExp, redScore > blueScore, km)
    newBlueElo = elo(blueRating, blueExp, blueScore > redScore, km)

    redPlayer.rating = newRedElo
    bluePlayer.rating = newBlueElo
    redPlayer.save()
    bluePlayer.save()
    
    return redirect(f'/l/{league_name}/')

def expected(A, B):
    """
    Calculate expected score of A in a match against B
    :param A: Elo rating for player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def elo(old, exp, score, k_mult=1, k=32):
    """
    Calculate the new Elo rating for a player
    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + (k*k_mult) * (score - exp)

def k_mult(diff, winRating, loseRating):
    #LN(ABS(PD)+1) * (2.2/((ELOW-ELOL)*.001+2.2))
    return math.log(abs(diff) + 1) * (2.2 / ((winRating - loseRating)*.001+2.2))