from gwcsa_heroku.models import CURRENT_SEASON

def constants(request):
    return {
        "current_season": CURRENT_SEASON,
    }
