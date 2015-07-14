import json
from django.views.generic import TemplateView
from resource_daily_scheduler.booking_req_views import AjaxableBookingRequestCreateView, ColorSchema
from resource_daily_scheduler.models import BookableResource
from resource_daily_scheduler.views import ResourceScheduleTemplateView

__author__ = 'weijia'


class ResourceTableScheduler(ResourceScheduleTemplateView):
    template_name = "resource_daily_scheduler/table_scheduler.html"
    # bookable_resource_class = BookableResource
    # get_schedule_url_name = 'get_schedule'
    # resource_permission_id = "resource_daily_scheduler.change_bookableresource"
    # # resource_detail = "update_resource/"
    # request_create_view = AjaxableBookingRequestCreateView
    #
    # def get_context_data(self, **kwargs):
    #     default_context = super(ResourceTableScheduler, self).get_context_data(**kwargs)
    #     resource_list_query = self.bookable_resource_class.objects.all()
    #     resource_list = []
    #     for resource in resource_list_query:
    #         resource_list.append({"id": str(resource.pk), "title": resource.get_title()})
    #     default_context["resource_list"] = json.dumps(resource_list)
    #     if self.request.user.has_perm(self.resource_permission_id):
    #         default_context["is_admin"] = "true"
    #     default_context["event_colors"] = json.dumps(self.get_colors())
    #     return default_context
