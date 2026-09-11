import contextlib
import json


class EncryptedPayloadMixin:
    """Mixin for CreateView/UpdateView: saves encrypted_payload from POST data.

    JS adds a hidden <input name="encrypted_payload"> to the form before submission.
    This mixin reads it, validates it as JSON, and sets it on the model instance
    before the normal save path runs.
    """

    def form_valid(self, form):
        raw = self.request.POST.get("encrypted_payload")
        if raw:
            with contextlib.suppress(json.JSONDecodeError, ValueError):
                form.instance.encrypted_payload = json.loads(raw)
        return super().form_valid(form)
