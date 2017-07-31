from django.shortcuts import redirect, render
from leagues.models import League, Match, Player, MatchParticipant
from elo import elo
import datetime, math
from django.utils import timezone

def home_page(request):
    return render(request, 'home.html')
    
def view_league(request, league_name):
    league_ = League.objects.get(name=league_name)

    origin = datetime.date(2017, 7, 7)
    fDoW = datetime.date.today() - datetime.timedelta(days=datetime.date.today().isoweekday() % 7)

    player_list = []
    record_list = dict()
    players = league_.players.order_by('-rating')
    for p in players:
        history = list(p.get_rating_history().filter(date_created__range=[origin, fDoW]).order_by('date_created'))

        tenDay = datetime.datetime.utcnow() - datetime.timedelta(days=10)
        if p.get_rating_history().order_by('-date_created')[0].date_created < tenDay.replace(tzinfo=timezone.utc):
            continue

        if len(history) > 0:
            last = p.rating - history[len(history) - 1].field_value 
        else:
            last = p.rating - 1500

        lastStr = diffStr = str(round(last, 0))
        if last > 0:
            lastStr = "+" + lastStr

        p_list = {'id': p.id, 'name': p.name, 'last': lastStr, 'rating': p.rating}
        player_list.append(p_list)
        record_list[p.name] = get_records(league_, p)

    playernames = list(players.values_list('name', flat=True))
    past_20_matches = league_.matches.order_by('-time')[:20]
    return render(request, 'league.html', {'league': league_, 
                                            'player_list': player_list, 
                                            'playernames' : playernames, 
                                            'matches' : past_20_matches,
                                            'records': record_list })
    
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

def get_records(league_, player):
    records = dict()
    for m in player.matches.all():
        if player.name == m.matchparticipant_set.all()[0].player.name:
            p_score = m.matchparticipant_set.all()[0].score
            o_score = m.matchparticipant_set.all()[1].score
            o_name = m.matchparticipant_set.all()[1].player.name
        else:
            p_score = m.matchparticipant_set.all()[1].score
            o_score = m.matchparticipant_set.all()[0].score
            o_name = m.matchparticipant_set.all()[0].player.name

        if p_score > o_score:
            val = 1
        else:
            val = -1

        records[o_name] = records.get(o_name, 0) + val

    return records

def view_player(request, league_name, player_id):
    league_ = League.objects.get(name=league_name)
    player = Player.objects.get(id=player_id)

    gp = player.matches.all()
    wins = 0
    losses = 0
    redwins = 0
    redlosses = 0
    bluewins = 0
    bluelosses = 0
    otwins = 0
    otlosses = 0
    for m in gp:
        if player.name == m.matchparticipant_set.all()[0].player.name:
            pl = m.matchparticipant_set.all()[0]
            opp = m.matchparticipant_set.all()[1]
        else:
            pl = m.matchparticipant_set.all()[1]
            opp = m.matchparticipant_set.all()[0]   

        if pl.score > opp.score: #Win
            wins = wins + 1
            if pl.wasRed:
                redwins = redwins + 1
            else:
                bluewins = bluewins + 1
            if pl.score + opp.score > 18:
                otwins = otwins +1
        else:                   #Loss
            losses = losses + 1
            if pl.wasRed:
                redlosses = redlosses + 1
            else:
                bluelosses = bluelosses + 1
            if pl.score + opp.score > 18:
                otlosses = otlosses + 1


    redStr = str(redwins) + "-" + str(redlosses)
    blueStr = str(bluewins) + "-" + str(bluelosses)
    otStr = str(otwins) + "-" + str(otlosses)
    past_50_matches = player.matches.order_by('-time')[:50]

    history = list(player.get_rating_history())
    history_dates = []
    history_values = []

    maxV = 0
    minV = 999999
    for i, h in enumerate(history):
        if i == 0:
            history_dates.append("Start")
        else:
            history_dates.append("Game " + str(i))
        history_values.append(h.field_value)
        if h.field_value > maxV:
            maxV = h.field_value
        if h.field_value < minV:
            minV = h.field_value

    maxV = math.ceil(maxV / 10.0) * 10.0
    minV = math.floor(minV / 10.0) * 10.0
    maxDiff = maxV - 1500
    minDiff = 1500 - minV
    if maxDiff > minDiff:
        minV = 1500 - maxDiff
    else:
        maxV = 1500 + minDiff
    return render(request, 'player.html', {'league': league_, 
                                            'player': player, 
                                            'gp': gp.count,
                                            'wins': wins,
                                            'losses': losses,
                                            'redStr': redStr,
                                            'blueStr': blueStr,
                                            'otStr': otStr,
                                            'matches': past_50_matches,
                                            'historyDates': history_dates,
                                            'historyValues': history_values,
                                            'maxV': maxV,
                                            'minV': minV},)