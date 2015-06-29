import json
import datetime
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, CreateView, View
import pytz
# from djangoautoconf.class_based_views.create_view_factory import get_ajax_create_view_from_model
from djangoautoconf.django_utils import retrieve_param
from resource_daily_scheduler.booking_req_views import AjaxableBookingRequestCreateView
from resource_daily_scheduler.models import BookableResource, BookingRequest, get_timezone_aware_datetime_from_date_str
from resource_daily_scheduler.resource_views import BookableResourceCreateView

__author__ = 'weijia'


class ResourceScheduleTemplateView(TemplateView):
    template_name = "resource_daily_scheduler/scheduler.html"
    bookable_resource_class = BookableResource
    get_schedule_url_name = 'get_schedule'
    resource_permission_id = "resource_daily_scheduler.change_bookingrequest"
    resource_detail = "update_resource/"
    resource_create_view_class = BookableResourceCreateView
    request_create_view = AjaxableBookingRequestCreateView

    def get_context_data(self, **kwargs):
        default_context = super(ResourceScheduleTemplateView, self).get_context_data(**kwargs)
        resource_list_query = self.bookable_resource_class.objects.all()
        resource_list = []
        for resource in resource_list_query:
            resource_list.append({"id": str(resource.pk), "title": resource.get_title()})
        default_context["resource_list"] = json.dumps(resource_list)
        default_context["resource_type"] = 'Test'
        default_context["get_schedule"] = reverse(self.get_schedule_url_name)

        default_context["new_resource_form"] = self.resource_create_view_class().get_form_class()

        default_context["booking_req_form"] = self.request_create_view().get_form_class()
        default_context["is_admin"] = "false"
        default_context["resource_detail"] = self.resource_detail

        if self.request.user.has_perm(self.resource_permission_id):
            default_context["is_admin"] = "true"
        return default_context


class GetScheduleView(View):
    booking_request_class = BookingRequest

    def get(self, request, *args, **kwargs):
        data = retrieve_param(request)
        tz = pytz.timezone("Asia/Shanghai")
        start = get_timezone_aware_datetime_from_date_str(data["start"])
        end = get_timezone_aware_datetime_from_date_str(data["end"])
        start_query = Q(end__lt=start)
        end_query = Q(start__gt=end)
        res_query = self.booking_request_class.objects.filter(~(end_query | start_query))
        res = []
        for event in res_query:
            color = "gray"
            if event.is_approved:
                color = "yellow"
            if event.is_ongoing:
                color = "green"
            res.append({"id": "%d" % event.pk, "resourceId": "%d" % event.resource.pk, "start": str(event.start),
                        "end": str(event.end), "title": event.project, "color": color})
        return HttpResponse(json.dumps(res), content_type="application/json")


class ApproveRequestView(View):
    booking_request_class = BookingRequest

    def get(self, request, *args, **kwargs):
        data = retrieve_param(request)
        req_id = data["requestId"]
        r = self.booking_request_class.objects.get(pk=int(req_id))
        if r.is_approved:
            r.is_approved = False
            result = "false"
        else:
            r.is_approved = True
            result = "true"
        r.save()
        return HttpResponse(json.dumps({"result": result}), content_type="application/json")
