from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from dashboard.models import SolarSensor


@login_required(login_url="/login/")
def index(request):
    if SolarSensor.objects.filter(user=request.user, external_id__isnull=False).count() < 3:
        SolarSensor.objects.get_or_create(
            user=request.user,
            external_id=1,
            defaults={"name": "Node 1", "location": "Panel → MPPT", "sensor_type": "ESP32"},
        )
        SolarSensor.objects.get_or_create(
            user=request.user,
            external_id=2,
            defaults={"name": "Node 2", "location": "MPPT → Battery", "sensor_type": "ESP32"},
        )
        SolarSensor.objects.get_or_create(
            user=request.user,
            external_id=3,
            defaults={"name": "Node 3", "location": "Battery → Inverter", "sensor_type": "ESP32"},
        )

    sensors = list(
        SolarSensor.objects.filter(user=request.user)
        .order_by('id')
        .values('id', 'external_id', 'name')
    )
    context = {'segment': 'index', 'sensors': sensors}

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
