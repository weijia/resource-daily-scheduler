from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import redirect_to
from djangoautoconf.class_based_views.create_view_factory import create_ajaxable_view_from_model
from resource_daily_scheduler.booking_req_views import AjaxableBookingRequestCreateView, \
    AjaxableBookingRequestUpdateView, GetScheduleView, ApproveRequestView
from resource_daily_scheduler.jquery_gantt_views import ResourceScheduleGanttView
from resource_daily_scheduler.models import BookableResource, BookingRequest
from resource_daily_scheduler.resource_views import ResourceAjaxMixin, ResourceViewFactory
from resource_daily_scheduler.table_scheduler import ResourceTableScheduler
from resource_daily_scheduler.views import ResourceScheduleTemplateView
from towel.modelview import ModelView

resource_views = ModelView(BookableResource)
resource_booking_req_views = ModelView(BookingRequest)
# resource_views_ajax = ModelView(BookableResource, base_template="modal.html")
# resource_booking_req_views_ajax = ModelView(BookingRequest, base_template="modal.html")


urlpatterns = patterns(
    '',
    url(r'^resources/', include(resource_views.urls)),
    url(r'^requests/', include(resource_booking_req_views.urls)),
    # url(r'^resources_ajax/', include(resource_views_ajax.urls)),
    # url(r'^requests_ajax/', include(resource_booking_req_views_ajax.urls)),
    url(r'^test/', login_required(ResourceScheduleTemplateView.as_view()), name="resource_scheduler"),
    url(r'^jquery_gantt$', login_required(ResourceScheduleGanttView.as_view()), name="resource_scheduler_jquery_gantt"),
    # url(r'^jquery_gantt$', login_required(ResourceScheduleGanttView.as_view()),
                                            # name="resource_scheduler_jquery_gantt"),
    # url(r'^table_schedule', login_required(ResourceTableScheduler.as_view()), name="resource_scheduler_jquery_gantt"),
    url(r'^$', login_required(ResourceTableScheduler.as_view()), name="resource_scheduler_jquery_gantt"),

    url(r'^get_schedule/', GetScheduleView.as_view(), name="get_schedule"),
    url(r'^approve_request/', ApproveRequestView.as_view(), name="approve_request"),

    url(r'^create_resource/',
        ResourceViewFactory(BookableResource).get_create_view_class().as_view(success_url="../"),
        name="create_resource"),

    url(r'^update_resource/(?P<pk>[0-9]+)/$',
        ResourceViewFactory(BookableResource).get_update_view_class().as_view(success_url="../"),
        name="update_resource"),
    # Used for returning from the above
    url(r'^update_resource/$', redirect_to, {'url': '../'}),

    url(r'^create_booking_req/', AjaxableBookingRequestCreateView.as_view(),
        name="create_booking_req"),

    url(r'^req_update/(?P<pk>[0-9]+)/$', login_required(AjaxableBookingRequestUpdateView.as_view()),
        name="request_update"),
    url(r'^req_update/$', redirect_to, {'url': '../'}),
    url(r'^req_update_ajax/(?P<pk>[0-9]+)/$', login_required(AjaxableBookingRequestUpdateView.as_view(
        template_name="ajax_base.html")),
        name="request_update_ajax"),
    # Used for returning from the above
    url(r'^req_update_ajax/$', redirect_to, {'url': '../'}),
)
