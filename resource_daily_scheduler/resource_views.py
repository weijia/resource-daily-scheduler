from django.views.generic import CreateView, UpdateView
from djangoautoconf.class_based_views.ajax_views import AjaxableResponseMixin, TowelTemplateMixin
from resource_daily_scheduler.models import BookableResource

__author__ = 'weijia'


class ResourceAjaxMixin(AjaxableResponseMixin):

    def get_result_dict(self):
        title = ""
        if hasattr(self.object, "get_title"):
            title = self.object.get_title()
        data = {
            'pk': self.object.pk,
            'title': title
        }
        return data


class BookableResourceCreateView(ResourceAjaxMixin,
                                 CreateView):
    model = BookableResource
    template_name = "form_view_base_template.html"

    def get_context_data(self, **kwargs):
        context = super(BookableResourceCreateView, self).get_context_data(**kwargs)
        context["submit_button"] = "Create"
        return context


class BookableResourceUpdateView(ResourceAjaxMixin,
                                 UpdateView):
    model = BookableResource
    template_name = "form_view_base_template.html"

    def get_context_data(self, **kwargs):
        context = super(BookableResourceUpdateView, self).get_context_data(**kwargs)
        context["submit_button"] = "Update"
        return context
