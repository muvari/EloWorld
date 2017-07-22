from django.shortcuts import redirect, render
from leagues.models import League, Match, Player, MatchParticipant
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
    past_20_matches = league_.matches.order_by('-time')[:200]
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

    redExp = expected(redRating, blueRating)
    blueExp = expected(blueRating, redRating)

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

    km = k_mult(adjustedDiff(diff), winRating, loseRating)

    newRedElo = elo(redRating, redExp, redScore > blueScore, km)
    newBlueElo = elo(blueRating, blueExp, blueScore > redScore, km)
    rmp.delta = newRedElo - redRating
    bmp.delta = newBlueElo - blueRating

    redPlayer.rating = newRedElo
    bluePlayer.rating = newBlueElo
    redPlayer.save()
    bluePlayer.save()
    rmp.save()
    bmp.save()
    
    return redirect(f'/l/{league_name}/')

def adjustedDiff(diff):
    if diff == 1:
        return 1.5
    elif diff == 2:
        return 1.6
    elif diff == 3:
        return 1.7
    elif diff == 4:
        return 1.8
    elif diff == 5:
        return 2
    elif diff == 6:
        return 2.3
    elif diff == 7:
        return 2.8
    elif diff == 8:
        return 3.6
    elif diff == 9:
        return 4.9
    else:
        return 7

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