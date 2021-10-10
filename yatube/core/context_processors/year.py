import datetime as dt


def year(request):
    current_year = dt.date.today().year
    return {'year': current_year}
