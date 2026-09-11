import json
from datetime import datetime

from dateutil import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from moodyduck.common.helpers import get_upload_path
from moodyduck.common.views import EncryptedPayloadMixin

from .forms import StatusForm
from .models import Activity, Mood, Status, StatusActivity, StatusMedia
from .statistics import (
    activitymood_data,
    activitypies_data,
    activitystats,
    moodpies_data,
    moodstats_data,
)


def _parse_enc_file_meta(request):
    raw = request.POST.get("encrypted_file_metadata", "[]")
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return []


class StatusListView(LoginRequiredMixin, ListView):
    template_name = "mood/status_list.html"
    model = Status

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Status List")
        context["subtitle"] = _("Just a list of your mood entries.")
        context["buttons"] = [
            (reverse_lazy("mood:status_create"), _("New Status"), "plus")
        ]
        context["payloads"] = {
            str(obj.id): obj.encrypted_payload
            for obj in context["object_list"]
            if obj.encrypted_payload
        }
        return context

    def get_queryset(self):
        status_list = Status.objects.filter(user=self.request.user).order_by(
            "timestamp"
        )

        if "from" in self.request.GET:
            from_timestamp = datetime.strptime(
                self.request.GET["from"], "%Y-%m-%d"
            ).replace(tzinfo=timezone.utc)
            status_list = status_list.filter(timestamp__gte=from_timestamp)

        if "to" in self.request.GET:
            to_timestamp = datetime.strptime(
                self.request.GET["to"], "%Y-%m-%d"
            ).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            status_list = status_list.filter(timestamp__lte=to_timestamp)

        return status_list


class StatusViewView(LoginRequiredMixin, DetailView):
    template_name = "mood/status_view.html"
    model = Status

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("View Status")
        context["subtitle"] = _("View the details of your mood entry.")
        context["buttons"] = [
            (
                reverse_lazy("mood:status_edit", kwargs={"id": self.kwargs["id"]}),
                _("Edit Status"),
                "pencil-simple",
            )
        ]
        context["media_list"] = [
            {
                "id": m.pk,
                "url": m.file.url,
                "ep": m.encrypted_payload,
                "name": m.basename,
            }
            for m in self.object.statusmedia_set.all()
        ]
        return context

    def get_object(self):
        return get_object_or_404(Status, user=self.request.user, id=self.kwargs["id"])


class StatusCreateView(EncryptedPayloadMixin, LoginRequiredMixin, CreateView):
    template_name = "mood/status_edit.html"
    form_class = StatusForm
    model = Status

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Status")
        context["subtitle"] = _("How are you feeling today?")
        context["scripts"] = [static("frontend/js/dropdown-to-buttons.js")]
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        ret = super().form_valid(form)

        for activity in form.cleaned_data["activities"]:
            if activity.user == self.request.user:
                StatusActivity.objects.create(activity=activity, status=form.instance)

        enc_meta = _parse_enc_file_meta(self.request)
        for i, attachment in enumerate(form.cleaned_data["uploads"]):
            dba = StatusMedia(status=form.instance)
            dba.file.save(get_upload_path(form.instance, attachment.name), attachment)
            if i < len(enc_meta):
                dba.encrypted_payload = enc_meta[i]
            dba.save()

        return ret

    def get_success_url(self):
        return reverse_lazy("mood:status_view", kwargs={"id": self.object.id})


class StatusEditView(EncryptedPayloadMixin, LoginRequiredMixin, UpdateView):
    template_name = "mood/status_edit.html"
    form_class = StatusForm
    model = Status

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Update Status")
        context["subtitle"] = _("Change a status you created before.")
        context["scripts"] = [static("frontend/js/dropdown-to-buttons.js")]
        context["buttons"] = [
            (
                reverse_lazy("mood:status_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete Status"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(Status, user=self.request.user, id=self.kwargs["id"])

    def form_valid(self, form):
        enc_meta = _parse_enc_file_meta(self.request)
        for i, attachment in enumerate(form.cleaned_data["uploads"]):
            dba = StatusMedia(status=form.instance)
            dba.file.save(get_upload_path(form.instance, attachment.name), attachment)
            if i < len(enc_meta):
                dba.encrypted_payload = enc_meta[i]
            dba.save()

        for activity in form.cleaned_data["activities"]:
            if (
                activity.user == self.request.user
                and activity not in form.instance.activity_set
            ):
                StatusActivity.objects.create(activity=activity, status=form.instance)

        for statusactivity in form.instance.statusactivity_set.all():
            if statusactivity.activity not in form.cleaned_data["activities"]:
                statusactivity.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mood:status_view", kwargs={"id": self.object.id})


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "mood/status_delete.html"
    model = Status

    def get_object(self):
        return get_object_or_404(Status, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("mood:status_list")


class ActivityListView(LoginRequiredMixin, ListView):
    template_name = "mood/activity_list.html"
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Activities")
        context["subtitle"] = _("The activities you have defined.")
        context["buttons"] = [
            (
                reverse_lazy("mood:activity_create"),
                _("Create Activity"),
                "pencil-simple",
            )
        ]
        context["payloads"] = {
            str(obj.id): obj.encrypted_payload
            for obj in context["object_list"]
            if obj.encrypted_payload
        }
        return context

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)


class ActivityEditView(EncryptedPayloadMixin, LoginRequiredMixin, UpdateView):
    template_name = "mood/activity_edit.html"
    model = Activity
    fields = ["name", "icon", "color", "hidden"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Activity")
        context["subtitle"] = _("Make changes to the activity.")
        context["scripts"] = [
            static("colorfield/jscolor/jscolor.js"),
            static("colorfield/colorfield.js"),
        ]
        return context

    def get_object(self):
        return get_object_or_404(Activity, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("mood:activity_list")


class ActivityCreateView(EncryptedPayloadMixin, LoginRequiredMixin, CreateView):
    template_name = "mood/activity_edit.html"
    model = Activity
    fields = ["name", "icon", "color"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Activity")
        context["subtitle"] = _("Add a new activity.")
        context["scripts"] = [
            static("colorfield/jscolor/jscolor.js"),
            static("colorfield/colorfield.js"),
        ]
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mood:activity_list")


class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "mood/activity_delete.html"
    model = Activity

    def get_object(self):
        return get_object_or_404(Activity, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("mood:activity_list")


class MoodListView(LoginRequiredMixin, ListView):
    template_name = "mood/mood_list.html"
    model = Mood

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Moods")
        context["subtitle"] = _("The different moods you have defined.")
        context["buttons"] = [
            (reverse_lazy("mood:mood_create"), _("Create Mood"), "pencil-simple")
        ]
        context["payloads"] = {
            str(obj.id): obj.encrypted_payload
            for obj in context["object_list"]
            if obj.encrypted_payload
        }
        return context

    def get_queryset(self):
        return Mood.objects.filter(user=self.request.user)


class MoodEditView(EncryptedPayloadMixin, LoginRequiredMixin, UpdateView):
    template_name = "mood/mood_edit.html"
    model = Mood
    fields = ["name", "icon", "color", "value"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Mood")
        context["subtitle"] = _("Make changes to the mood.")
        context["scripts"] = [
            static("colorfield/jscolor/jscolor.js"),
            static("colorfield/colorfield.js"),
        ]
        return context

    def get_object(self):
        return get_object_or_404(Mood, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("mood:mood_list")


class MoodCreateView(EncryptedPayloadMixin, LoginRequiredMixin, CreateView):
    template_name = "mood/mood_edit.html"
    model = Mood
    fields = ["name", "icon", "color", "value"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Activity")
        context["subtitle"] = _("Add a new activity.")
        context["scripts"] = [
            static("colorfield/jscolor/jscolor.js"),
            static("colorfield/colorfield.js"),
        ]
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mood:activity_list")


class MoodStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mood/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Statistics")
        context["activities"] = activitystats(self.request.user)
        context["mood_chart"] = json.dumps(moodstats_data(self.request.user))
        context["pies_chart"] = json.dumps(moodpies_data(self.request.user))
        return context


class MoodCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        res = HttpResponse(content_type="text/csv")
        res["content-disposition"] = 'filename="mood.csv"'

        startdate = request.GET.get("start")
        enddate = request.GET.get("end")

        maxdate = None
        mindate = None

        if enddate:
            maxdate = datetime.strptime(enddate, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )

            if not startdate:
                mindate = maxdate - relativedelta.relativedelta(weeks=1)

        if startdate:
            mindate = datetime.strptime(startdate, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )

            if not enddate:
                maxdate = mindate + relativedelta.relativedelta(weeks=1)

        if not maxdate:
            maxdate = timezone.now()
            mindate = maxdate - relativedelta.relativedelta(weeks=1)

        output = "date,value"

        for status in Status.objects.filter(
            user=request.user, timestamp__gte=mindate, timestamp__lte=maxdate
        ):
            if status.mood:
                date = status.timestamp.strftime("%Y-%m-%d %H:%M")
                output += f"\n{date},{status.mood.value}"

        res.write(output)
        return res


class MoodPlotView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(moodstats_data(request.user))


class MoodPiesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(moodpies_data(request.user))


class ActivityStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mood/statistics_activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = get_object_or_404(Activity, user=self.request.user, id=kwargs["id"])
        context["title"] = _("Activity Statistics for %s") % activity.name
        context["activity"] = activity
        context["mood_chart"] = json.dumps(activitymood_data(activity))
        context["pies_chart"] = json.dumps(activitypies_data(activity))
        return context


class ActivityPlotView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        activity = get_object_or_404(Activity, user=request.user, id=kwargs["id"])
        return JsonResponse(activitymood_data(activity))


class ActivityPiesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        activity = get_object_or_404(Activity, user=request.user, id=kwargs["id"])
        return JsonResponse(activitypies_data(activity))


class MoodCountHeatmapJSONView(LoginRequiredMixin, View):
    """Returns a JSON object with the mood entries for a given time period.

    This is used in conjunction with the Cal-Heatmap library to display a
    heatmap of mood entries.
    """

    def get(self, request, *args, **kwargs):
        res = HttpResponse(content_type="application/json")

        start = request.GET.get("start")
        end = request.GET.get("end")

        if end:
            maxdate = datetime.strptime(end, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
        else:
            maxdate = timezone.now()

        if start:
            mindate = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            mindate = maxdate - relativedelta.relativedelta(years=1)

        data = Status.objects.filter(
            user=request.user, timestamp__gte=mindate, timestamp__lte=maxdate
        )

        output = {}

        for entry in data:
            date = entry.timestamp.strftime("%Y-%m-%d")

            if date not in output:
                output[date] = {"count": 0, "total": 0, "moodcount": 0}

            if entry.mood:
                output[date]["total"] += entry.mood.value
                output[date]["moodcount"] += 1

            output[date]["count"] += 1

        output = [
            {
                "date": key,
                "count": value["count"],
                "average": (
                    (value["total"] / value["moodcount"])
                    if value["moodcount"] > 0
                    else 0
                ),
            }
            for key, value in output.items()
        ]

        res.write(json.dumps(output))

        return res


class MoodHeatmapValuesJSONView(LoginRequiredMixin, View):
    """Returns a JSON object with the available mood values.

    This is used to display the correct colors in the heatmap.
    """

    def get(self, request, *args, **kwargs):
        res = HttpResponse(content_type="application/json")

        data = Mood.objects.filter(user=request.user)

        output = {
            entry.value: {"name": entry.name, "icon": entry.icon, "color": entry.color}
            for entry in data
        }

        res.write(json.dumps(output))

        return res
