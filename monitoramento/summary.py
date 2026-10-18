import math


def summarize(events):
    """Somar intervalos já normalizados e sem sobreposição, excluindo inatividade."""
    totals = {}
    for event in events:
        app, seconds, afk = event["app"], event["seconds"], event["afk"]
        if not isinstance(app, str) or not app.strip():
            raise ValueError("app deve ser um nome não vazio")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise ValueError("seconds deve ser numérico")
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("seconds deve ser finito e não negativo")
        if not isinstance(afk, bool):
            raise ValueError("afk deve ser booleano")
        if not afk:
            totals[app] = totals.get(app, 0) + seconds
    return totals
