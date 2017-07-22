import math

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