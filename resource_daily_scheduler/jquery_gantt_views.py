from django.views.generic import TemplateView

__author__ = 'weijia'


class ResourceScheduleGanttView(TemplateView):
    template_name = "resource_daily_scheduler/index_jquery_gantt.html"
