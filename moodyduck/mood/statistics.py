from math import pi  # noqa: F401 — kept for potential future use
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .models import Status, Mood, StatusActivity


def _rolling_mean(values, window=7):
    result = []
    for i in range(len(values)):
        chunk = values[max(0, i - window + 1) : i + 1]
        result.append(sum(chunk) / len(chunk))
    return result


def moodstats_data(user):
    entries = []
    for status in (
        Status.objects.filter(user=user)
        .select_related("mood")
        .order_by("timestamp")
    ):
        if status.mood:
            entries.append(
                {
                    "x": int(status.timestamp.timestamp() * 1000),
                    "y": status.mood.value,
                    "color": status.mood.color,
                    "label": status.mood.name,
                }
            )

    avgs = _rolling_mean([e["y"] for e in entries])
    average = [
        {"x": entries[i]["x"], "y": round(avgs[i], 2)} for i in range(len(entries))
    ]
    return {"points": entries, "average": average}


def moodpies_data(user):
    now = timezone.now()
    periods = {
        "weekly": now - relativedelta(weeks=1),
        "monthly": now - relativedelta(months=1),
        "yearly": now - relativedelta(years=1),
    }
    moods = list(Mood.objects.filter(user=user))
    result = {}
    for period_name, since in periods.items():
        counts = {m.name: 0 for m in moods}
        for status in Status.objects.filter(
            user=user, timestamp__gte=since
        ).select_related("mood"):
            if status.mood:
                counts[status.mood.name] += 1
        result[period_name] = {
            "labels": [m.name for m in moods],
            "data": [counts[m.name] for m in moods],
            "colors": [m.color for m in moods],
        }
    return result


def activitystats(user):
    output = {}
    for status in Status.objects.filter(user=user):
        for activity in status.activity_set:
            if activity not in output:
                output[activity] = {
                    "alltime": 0,
                    "yearly": 0,
                    "monthly": 0,
                    "weekly": 0,
                }
            output[activity]["alltime"] += 1
            if status.timestamp > timezone.now() - relativedelta(years=1):
                output[activity]["yearly"] += 1
            if status.timestamp > timezone.now() - relativedelta(months=1):
                output[activity]["monthly"] += 1
            if status.timestamp > timezone.now() - relativedelta(weeks=1):
                output[activity]["weekly"] += 1
    return output


def activitymood_data(activity):
    entries = []
    for sa in (
        StatusActivity.objects.filter(activity=activity)
        .select_related("status__mood")
        .order_by("status__timestamp")
    ):
        if sa.status.mood:
            entries.append(
                {
                    "x": int(sa.status.timestamp.timestamp() * 1000),
                    "y": sa.status.mood.value,
                    "color": sa.status.mood.color,
                    "label": sa.status.mood.name,
                }
            )

    avgs = _rolling_mean([e["y"] for e in entries])
    average = [
        {"x": entries[i]["x"], "y": round(avgs[i], 2)} for i in range(len(entries))
    ]
    return {"points": entries, "average": average}


def activitypies_data(activity):
    now = timezone.now()
    periods = {
        "weekly": now - relativedelta(weeks=1),
        "monthly": now - relativedelta(months=1),
        "yearly": now - relativedelta(years=1),
    }
    moods = list(Mood.objects.filter(user=activity.user))
    result = {}
    for period_name, since in periods.items():
        counts = {m.name: 0 for m in moods}
        for sa in StatusActivity.objects.filter(
            activity=activity, status__timestamp__gte=since
        ).select_related("status__mood"):
            if sa.status.mood:
                counts[sa.status.mood.name] += 1
        result[period_name] = {
            "labels": [m.name for m in moods],
            "data": [counts[m.name] for m in moods],
            "colors": [m.color for m in moods],
        }
    return result
