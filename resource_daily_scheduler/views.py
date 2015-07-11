import json
import datetime
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, CreateView, View
import pytz
# from djangoautoconf.class_based_views.create_view_factory import get_ajax_create_view_from_model
from djangoautoconf.class_based_views.form_factory import ModelFormFactory
from djangoautoconf.django_utils import retrieve_param
from resource_daily_scheduler.booking_req_views import AjaxableBookingRequestCreateView
from resource_daily_scheduler.models import BookableResource, BookingRequest, get_timezone_aware_datetime_from_date_str
# from resource_daily_scheduler.resource_views import BookableResourceCreateView, ModelFormFactory

__author__ = 'weijia'


class ColorSchema(object):
    WAITING_FOR_YOUR_APPROVAL_COLOR = "red"
    WAITING_FOR_APPROVAL_FROM_OTHERS_COLOR = "gray"
    APPROVED_COLOR = "blue"
    ONGOING_COLOR = "green"


class ResourceScheduleTemplateView(TemplateView, ColorSchema):
    template_name = "resource_daily_scheduler/scheduler.html"
    bookable_resource_class = BookableResource
    get_schedule_url_name = 'get_schedule'
    resource_permission_id = "resource_daily_scheduler.change_bookingrequest"
    resource_detail = "update_resource/"
    # resource_create_view_class = BookableResourceCreateView
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

        # default_context["new_resource_form"] = self.resource_create_view_class().get_form_class()
        form_factory = ModelFormFactory(self.bookable_resource_class)
        form_factory.set_exclude("approver")
        default_context["new_resource_form"] = form_factory.get_form_class()()

        default_context["booking_req_form"] = self.request_create_view().get_form_class()
        default_context["is_admin"] = "false"
        default_context["resource_detail"] = self.resource_detail
        default_context["color_for_need_approval_from_others"] = self.WAITING_FOR_APPROVAL_FROM_OTHERS_COLOR
        default_context["color_for_approved"] = self.APPROVED_COLOR
        default_context["color_for_ongoing"] = self.ONGOING_COLOR
        default_context["color_for_need_your_approval"] = self.WAITING_FOR_YOUR_APPROVAL_COLOR

        if self.request.user.has_perm(self.resource_permission_id):
            default_context["is_admin"] = "true"
        return default_context


class GetScheduleView(View, ColorSchema):
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
            color = self.WAITING_FOR_APPROVAL_FROM_OTHERS_COLOR
            if event.is_approved:
                color = self.APPROVED_COLOR
            elif self.request.user.has_perm("change_bookableresource", event.resource):
                color = self.WAITING_FOR_YOUR_APPROVAL_COLOR
            if event.is_ongoing:
                color = self.ONGOING_COLOR
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
