import json
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from djangoautoconf.class_based_views.form_factory import ModelFormFactory
from resource_daily_scheduler.booking_req_views import AjaxableBookingRequestCreateView, ColorSchema
from resource_daily_scheduler.models import BookableResource

__author__ = 'weijia'


class ResourceScheduleTemplateView(TemplateView, ColorSchema):
    template_name = "resource_daily_scheduler/scheduler.html"
    bookable_resource_class = BookableResource
    get_schedule_url_name = 'get_schedule'
    resource_permission_id = "resource_daily_scheduler.change_bookableresource"
    resource_detail = "update_resource/"
    # resource_create_view_class = BookableResourceCreateView
    request_create_view = AjaxableBookingRequestCreateView
    page_title = "Resource Reservation System"
    resource_title = "Resources"

    def get_context_data(self, **kwargs):
        default_context = super(ResourceScheduleTemplateView, self).get_context_data(**kwargs)
        resource_list_query = self.bookable_resource_class.objects.all()
        resource_list = []
        for resource in resource_list_query:
            resource_list.append({"id": str(resource.pk), "title": resource.get_title()})
        default_context["resource_list"] = json.dumps(resource_list)
        default_context["resource_type"] = self.resource_title
        default_context["get_schedule"] = reverse(self.get_schedule_url_name)

        # default_context["new_resource_form"] = self.resource_create_view_class().get_form_class()
        form_factory = ModelFormFactory(self.bookable_resource_class)
        form_factory.set_exclude("approver")
        default_context["new_resource_form"] = form_factory.get_form_class()()

        default_context["booking_req_form"] = self.request_create_view().get_form_class()
        default_context["resource_detail"] = self.resource_detail
        # default_context["color_for_need_approval_from_others"] = self.WAITING_FOR_APPROVAL_FROM_OTHERS_COLOR
        # default_context["color_for_approved"] = self.APPROVED_COLOR
        # default_context["color_for_ongoing"] = self.ONGOING_COLOR
        # default_context["color_for_need_your_approval"] = self.WAITING_FOR_YOUR_APPROVAL_COLOR
        default_context["event_colors"] = json.dumps(self.get_colors())

        default_context["is_admin"] = "false"
        default_context["page_title"] = self.page_title
        if self.request.user.has_perm(self.resource_permission_id):
            default_context["is_admin"] = "true"
        return default_context
