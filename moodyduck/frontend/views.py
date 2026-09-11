from pathlib import Path

from django.http import FileResponse, HttpResponse
from django.views import View

_SPA_DIR = Path(__file__).resolve().parent.parent / "spa"


class SpaView(View):
    def get(self, request, *args, **kwargs):
        index = _SPA_DIR / "index.html"
        if not index.exists():
            return HttpResponse(
                "<h1>Frontend not built</h1>"
                "<p>Run <code>cd moodyduck/spa_src && npm run build</code> to build the SPA.</p>",
                content_type="text/html",
                status=503,
            )
        return FileResponse(open(index, "rb"), content_type="text/html")


class ServiceWorkerView(View):
    def get(self, request):
        sw = _SPA_DIR / "sw.js"
        if not sw.exists():
            return HttpResponse(status=404)
        response = FileResponse(open(sw, "rb"), content_type="text/javascript")  # noqa: SIM115
        response["Service-Worker-Allowed"] = "/"
        response["Cache-Control"] = "no-store"
        return response
