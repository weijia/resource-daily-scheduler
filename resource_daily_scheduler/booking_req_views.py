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
        exclude = ["is_approved", "requester", "approver", "is_ongoing", "is_completed", "is_canceled"]


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
        conflicts_filter = conflicts.filter(~Q(id=approval_request.pk) & (Q(is_approved=True) | Q(is_ongoing=True)))
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
    create_resource_permission = 'change_bookableresource'

    def form_valid(self, form):
        candidate = form.save(commit=False)
        candidate.approver = self.request.user
        candidate.save()
        assign_perm(self.create_resource_permission, self.request.user, candidate)
        # In ModelFormMixin.form_valid, form.save() and its parent's form_valid will be called
        # And in FormMixin (ModelFormMixin's parent) HttpResponseRedirect(self.get_success_url()) will be called
        response = super(ResourceApproverUpdater, self).form_valid(form)
        return response


class ColorSchema(object):
    COLOR_0_YOUR_REQUEST = "tomato"
    COLOR_1_WAITING_FOR_YOUR_APPROVAL = "yellow"
    COLOR_2_WAITING_FOR_APPROVAL_FROM_OTHERS = "limegreen"
    COLOR_3_APPROVED_COMMA_YOU_CAN_CHANGE = "DeepPink"
    COLOR_4_APPROVED_COMMA_YOU_CANNOT_CHANGE = "blue"
    COLOR_5_ONGOING = "green"
    # COLOR_CONFLICT = "DarkGray"  # "black"
    COLOR_6_COMPLETED = "aqua"
    COLOR_7_CANCELED = "grey"

    def get_colors(self):
        colors = {}
        for attr in dir(ColorSchema):
            if attr != attr.upper():
                continue
            if attr[:6] != "COLOR_":
                continue
            value = getattr(ColorSchema, attr)
            index = int(attr[6])
            attr_name = attr[8:]
            attr_name = attr_name.replace("_COMMA", ",")
            attr_name = attr_name.lower()
            attr_name = attr_name.replace("_", " ")
            colors[attr_name.capitalize()] = (index, value)
        return colors


class GetScheduleView(View, ColorSchema, RequestApprovalMixin):
    model = BookingRequest
    resource_approval_permission = "change_bookableresource"

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
            event = {"id": "%d" % event.pk, "resourceId": "%d" % event.resource.pk, "start": str(event.start),
                     "end": str(event.end), "title": event.project, "color": color}
            if color in [self.COLOR_1_WAITING_FOR_YOUR_APPROVAL,  self.COLOR_5_ONGOING,
                         self.COLOR_3_APPROVED_COMMA_YOU_CAN_CHANGE, self.COLOR_0_YOUR_REQUEST]:
                event["className"] = "todo"
            res.append(event)
        return HttpResponse(json.dumps(res), content_type="application/json")

    def get_color(self, event):
        color = self.COLOR_2_WAITING_FOR_APPROVAL_FROM_OTHERS
        has_perm = self.has_permission_to_manage_resource(event)
        if event.is_canceled:
            color = self.COLOR_7_CANCELED
        elif event.is_completed:
            color = self.COLOR_6_COMPLETED
        elif event.is_ongoing:
            # tz = pytz.timezone("Asia/Shanghai")
            # end_datetime = event.end
            # if event.end < end_datetime.astimezone(tz):
            #     color = self.COLOR_5_ONGOING
            color = self.COLOR_5_ONGOING
        elif event.is_approved:
            if has_perm:
                color = self.COLOR_3_APPROVED_COMMA_YOU_CAN_CHANGE
            else:
                color = self.COLOR_4_APPROVED_COMMA_YOU_CANNOT_CHANGE
        elif has_perm:
            if self.is_request_can_be_approved(event):
                color = self.COLOR_1_WAITING_FOR_YOUR_APPROVAL
                # else:
                #     color = self.COLOR_CONFLICT
        elif event.requester == self.request.user:
            color = self.COLOR_0_YOUR_REQUEST

        return color

    def has_permission_to_manage_resource(self, event):
        return self.request.user.has_perm(self.resource_approval_permission, event.resource)


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
