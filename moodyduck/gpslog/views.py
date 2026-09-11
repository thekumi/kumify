from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from moodyduck.keystore.crypto import encrypt_for_user
from moodyduck.keystore.models import UserKeyPair

from .models import GPSPoint, GPSToken, GPSTrack


class GPSLogView(View):
    def dispatch(self, request, *args, **kwargs):
        self.gps_track = get_object_or_404(GPSTrack, id=self.kwargs["track"])
        self.gps_token = get_object_or_404(
            GPSToken, track=self.gps_track, token=self.kwargs["token"]
        )
        return super().dispatch(request, *args, **kwargs)

    def _ingest(self, params):
        if not self.gps_token.write:
            return HttpResponse(status=403)

        if "lat" not in params or "lon" not in params:
            return HttpResponse(status=400)

        user = self.gps_track.user
        try:
            key_pair = UserKeyPair.objects.get(user=user)
        except UserKeyPair.DoesNotExist:
            return HttpResponse(
                "Encryption key not configured. Log in on a device first.",
                status=412,
            )

        fields = {"latitude": params["lat"], "longitude": params["lon"]}
        if params.get("alt"):
            fields["altitude"] = params["alt"]
        if params.get("spd"):
            fields["speed"] = params["spd"]
        if params.get("dir"):
            fields["bearing"] = params["dir"]

        tst = params.get("tst")
        try:
            timestamp = timezone.datetime.fromtimestamp(float(tst), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            timestamp = timezone.now()

        GPSPoint.objects.create(
            track=self.gps_track,
            token=self.gps_token,
            timestamp=timestamp,
            battery=params.get("batt") or None,
            accuracy=params.get("acc") or None,
            satellites=params.get("sat") or None,
            user_agent=self.request.META.get("HTTP_USER_AGENT") or None,
            encrypted_payload=encrypt_for_user(key_pair.public_key, fields),
        )
        return HttpResponse(status=201)

    def get(self, request, *args, **kwargs):
        return self._ingest(request.GET)

    def post(self, request, *args, **kwargs):
        return self._ingest(request.POST)
