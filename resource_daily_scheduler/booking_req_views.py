import json
from compat import View
import datetime
from django import forms
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
import pytz
from djangoautoconf.class_based_views.ajax_views import AjaxableResponseMixin
from djangoautoconf.class_based_views.create_view_factory import AjaxableFormContextUpdateMixin
from djangoautoconf.django_utils import retrieve_param
from guardian.shortcuts import assign_perm
from resource_daily_scheduler.models import BookingRequest, get_timezone_aware_datetime_from_date_str


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


class RequestApprovalMixin(object):
    def is_request_can_be_approved(self, approval_request):
        conflicts = self.model.objects.filter(
            start__lt=approval_request.end,
            end__gte=approval_request.start,
            resource=approval_request.resource,
        )
        conflicts_filter = conflicts.filter(~Q(id=approval_request.pk)&(Q(is_approved=True)|Q(is_ongoing=True)))
        # if any(conflicts_filter):
        #     return False
        for i in conflicts_filter:
            return False
        return True

    def is_valid_approval(self, approval_request):
        return (approval_request.approver is None) and approval_request.is_approved and \
               self.is_request_can_be_approved(approval_request)


class AjaxableBookingRequestUpdateView(AjaxableResponseMixin, AjaxableFormContextUpdateMixin, RequestApprovalMixin,
                                       UpdateView):
    form_class = BookingRequestUpdateForm
    model = BookingRequest
    ajax_form_id = "bookingReqEditForm"
    template_name = "form_view_base_template.html"
    submit_button_text = "Update"
    success_url = "../"

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
        if self.is_valid_approval(candidate):
            candidate.approver = self.request.user
            candidate.save()
        else:
            candidate.is_approved = False
        # In ModelFormMixin.form_valid, form.save() and its parent's form_valid will be called
        # And in FormMixin (ModelFormMixin's parent) HttpResponseRedirect(self.get_success_url()) will be called
        response = super(AjaxableBookingRequestUpdateView, self).form_valid(form)
        return response


class ResourceApproverUpdater(object):
    def form_valid(self, form):
        candidate = form.save(commit=False)
        candidate.approver = self.request.user
        candidate.save()
        assign_perm('change_bookableresource', self.request.user, candidate)
        # In ModelFormMixin.form_valid, form.save() and its parent's form_valid will be called
        # And in FormMixin (ModelFormMixin's parent) HttpResponseRedirect(self.get_success_url()) will be called
        response = super(ResourceApproverUpdater, self).form_valid(form)
        return response


class ColorSchema(object):
    COLOR_WAITING_FOR_YOUR_APPROVAL = "red"
    COLOR_WAITING_FOR_APPROVAL_FROM_OTHERS = "gray"
    COLOR_APPROVED = "blue"
    COLOR_ONGOING = "green"
    COLOR_CONFLICT = "black"
    COLOR_CAN_BE_SET_TO_ONGOING = "DarkSlateGray"

    def get_colors(self):
        colors = {}
        for attr in dir(ColorSchema):
            if attr != attr.upper():
                continue
            if attr[:6] != "COLOR_":
                continue
            value = getattr(ColorSchema, attr)
            attr_name = attr[6:].lower()
            attr_name = attr_name.replace("_", " ")
            colors[attr_name.capitalize()] = value
        return colors


# color_schema = {"Waiting for your approval": "red",
#                 "Waiting for approval from others": "gray",
#                 "Approved": "blue",
#                 "On going": "green",
#                 "Conflicted": "black",
#                 "Approved, can be set to ongoing": "DarkSlateGray"
#                 }


class GetScheduleView(View, ColorSchema, RequestApprovalMixin):
    model = BookingRequest
    # color_schema = {"Waiting for your approval": "red",
    #                 "Waiting for approval from others": "gray",
    #                 "Approved": "blue",
    #                 "On going": "green",
    #                 "Conflicted": "black",
    #                 "Approved, can be set to ongoing": "DarkSlateGray"
    #                 }

    def get(self, request, *args, **kwargs):
        data = retrieve_param(request)
        tz = pytz.timezone("Asia/Shanghai")
        start = get_timezone_aware_datetime_from_date_str(data["start"])
        end = get_timezone_aware_datetime_from_date_str(data["end"])
        start_query = Q(end__lt=start)
        end_query = Q(start__gt=end)
        res_query = self.model.objects.filter(~(end_query | start_query))
        res = []
        for event in res_query:
            color = self.get_color(event)
            res.append({"id": "%d" % event.pk, "resourceId": "%d" % event.resource.pk, "start": str(event.start),
                        "end": str(event.end), "title": event.project, "color": color})
        return HttpResponse(json.dumps(res), content_type="application/json")

    def get_color(self, event):
        color = self.COLOR_WAITING_FOR_APPROVAL_FROM_OTHERS
        has_perm = self.request.user.has_perm("change_bookableresource", event.resource)
        if event.is_approved:
            if has_perm:
                color = self.COLOR_CAN_BE_SET_TO_ONGOING
            else:
                color = self.COLOR_APPROVED
        elif has_perm:
            if self.is_request_can_be_approved(event):
                color = self.COLOR_WAITING_FOR_YOUR_APPROVAL
            else:
                color = self.COLOR_CONFLICT
        if event.is_ongoing:
            color = self.COLOR_ONGOING
        return color


class ApproveRequestView(View, RequestApprovalMixin):
    model = BookingRequest

    def get(self, request, *args, **kwargs):
        data = retrieve_param(request)
        req_id = data["requestId"]
        r = self.model.objects.get(pk=int(req_id))
        if r.is_approved:
            r.is_approved = False
            result = "false"
        else:
            r.is_approved = True
            result = "true"
        r.save()
        return HttpResponse(json.dumps({"result": result}), content_type="application/json")
