from compat import JsonResponse
import datetime
from django import forms
from django.views.generic.edit import CreateView, UpdateView
import pytz
from djangoautoconf.class_based_views.ajax_views import AjaxableResponseMixin, AjaxableViewMixin, TowelTemplateMixin
from djangoautoconf.class_based_views.create_view_factory import AjaxableFormContextUpdateMixin
from djangoautoconf.django_utils import retrieve_param
from resource_daily_scheduler.models import BookingRequest, BookableResource


class BookingRequestForm(forms.ModelForm):
    start = forms.DateField(
        required=False, widget=forms.TextInput(attrs={
            'class': 'datepicker'
        }))

    end = forms.DateField(
        required=False, widget=forms.TextInput(attrs={
            'class': 'datepicker'
        }))

    class Meta:
        model = BookingRequest
        exclude = ["is_approved", "requester", "approver", "is_ongoing"]


class BookingRequestUpdateForm(BookingRequestForm):
    class Meta:
        model = BookingRequest
        exclude = ["requester", "approver"]


class AjaxableBookingRequestCreateView(AjaxableResponseMixin, AjaxableFormContextUpdateMixin,
                                       CreateView):
    form_class = BookingRequestForm
    template_name = "form_view_base_template.html"
    submit_button_text = "Create"

    def get_form_kwargs(self):
        """
        Used to update end date in UI, as the end date in UI is included in the reservation
        :return:
        """
        kwargs = super(AjaxableBookingRequestCreateView, self).get_form_kwargs()
        # kwargs.update({"prefix": "update"})
        # tz = pytz.timezone("Asia/Shanghai")
        # kwargs["instance"].start = kwargs["instance"].start.astimezone(tz).strftime("%m/%d/%Y")
        # kwargs["instance"].end = (kwargs["instance"].end-datetime.timedelta(
        #     days=1)).astimezone(tz).strftime("%m/%d/%Y")
        data = retrieve_param(self.request)
        if ("start" in data) and ("resourceId" in data):
            kwargs["initial"] = {"start": data["start"], "resource": int(data["resourceId"])}
        return kwargs

    def form_valid(self, form):
        candidate = form.save(commit=False)
        candidate.requester = self.request.user  # use your own profile here
        candidate.save()
        response = super(AjaxableBookingRequestCreateView, self).form_valid(form)
        return response


class AjaxableBookingRequestUpdateView(AjaxableResponseMixin, AjaxableFormContextUpdateMixin,
                                       UpdateView):
    form_class = BookingRequestUpdateForm
    model = BookingRequest
    ajax_form_id = "bookingReqEditForm"
    template_name = "form_view_base_template.html"
    submit_button_text = "Update"
    success_url="../"

    def get_form_kwargs(self):
        """
        Used to update end date in UI, as the end date in UI is included in the reservation
        :return:
        """
        kwargs = super(AjaxableBookingRequestUpdateView, self).get_form_kwargs()
        kwargs.update({"prefix": "update"})
        tz = pytz.timezone("Asia/Shanghai")
        kwargs["instance"].start = kwargs["instance"].start.astimezone(tz).strftime("%m/%d/%Y")
        kwargs["instance"].end = (kwargs["instance"].end - datetime.timedelta(
            days=1)).astimezone(tz).strftime("%m/%d/%Y")
        return kwargs

    def form_valid(self, form):
        candidate = form.save(commit=False)
        if (candidate.approver is None) and candidate.is_approved:
            candidate.approver = self.request.user
            candidate.save()
        response = super(AjaxableBookingRequestUpdateView, self).form_valid(form)
        return response
