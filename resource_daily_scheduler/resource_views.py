# from django.forms import ModelForm
# from django.views.generic import CreateView, UpdateView, FormView
from djangoautoconf.class_based_views.ajax_views import AjaxableResponseMixin
from djangoautoconf.class_based_views.create_view_factory import AjaxableFormContextUpdateMixin
from djangoautoconf.class_based_views.form_factory import ModelFormFactory
from djangoautoconf.class_based_views.template_view_factory import TemplateViewFactory, force_list
from resource_daily_scheduler.booking_req_views import ResourceApproverUpdater
# from resource_daily_scheduler.models import BookableResource

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


# class BookableResourceCreateView(ResourceAjaxMixin,
#                                  CreateView):
#     model = BookableResource
#     template_name = "form_view_base_template.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(BookableResourceCreateView, self).get_context_data(**kwargs)
#         context["submit_button"] = "Create"
#         return context


# class BookableResourceUpdateView(ResourceAjaxMixin,
#                                  UpdateView):
#     model = BookableResource
#     template_name = "form_view_base_template.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(BookableResourceUpdateView, self).get_context_data(**kwargs)
#         context["submit_button"] = "Update"
#         return context


class ResourceViewFactory(object):
    def __init__(self, base_resource_model_class):
        super(ResourceViewFactory, self).__init__()
        self.__base_resource_model_class = base_resource_model_class

    def get_create_view_class(self):
        f = self.get_template_view_factory()
        f.add_parent_class(ResourceAjaxMixin)
        f.set_generic_template_view("Create")
        return f.get_view()

    def get_update_view_class(self):
        f = self.get_template_view_factory()
        f.set_generic_template_view("Update")
        return f.get_view()

    def get_template_view_factory(self):
        f = TemplateViewFactory()
        f.set_exclude(["approver"])
        f.add_parent_class([AjaxableFormContextUpdateMixin, ResourceApproverUpdater, ])
        f.set_model_class(self.__base_resource_model_class)
        model_factory = ModelFormFactory(self.__base_resource_model_class)
        model_factory.set_exclude(["approver"])
        form_class = model_factory.get_form_class()
        f.set_form_class(form_class)
        return f
