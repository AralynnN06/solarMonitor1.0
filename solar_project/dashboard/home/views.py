from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json

from dashboard.esp_state import LATEST


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@require_http_methods(["POST"])
def chat(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"reply": "Send a message and I’ll respond."})

    latest_payload = LATEST.get("payload")
    last_seen = LATEST.get("last_seen")

    lowered = message.lower()
    if "latest" in lowered or "reading" in lowered or "sensor" in lowered:
        if latest_payload is None:
            reply = "I don’t have any ESP32 data yet. POST to /api/esp/ingest/ first."
        else:
            reply = json.dumps({"last_seen": last_seen, "payload": latest_payload}, indent=2)
        return JsonResponse({"reply": reply})

    if "status" in lowered or "connected" in lowered:
        reply = "Connected" if last_seen else "Not connected"
        if last_seen:
            reply = f"Connected (last seen: {last_seen})"
        return JsonResponse({"reply": reply})

    if latest_payload and any(key in lowered for key in ["power", "voltage", "current"]):
        voltage = latest_payload.get("voltage")
        current = latest_payload.get("current")
        power = latest_payload.get("power")
        computed_power = None
        try:
            if power is None and voltage is not None and current is not None:
                computed_power = float(voltage) * float(current)
        except Exception:
            computed_power = None

        reply_payload = {
            "last_seen": last_seen,
            "voltage": voltage,
            "current": current,
            "power": power,
            "computed_power": computed_power,
        }
        return JsonResponse({"reply": json.dumps(reply_payload, indent=2)})

    return JsonResponse({
        "reply": "Try: 'status', 'latest', or 'power/voltage/current'."
    })
