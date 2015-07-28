import datetime
from django.contrib.auth.models import User
from django.db import models
import pytz


def get_timezone_aware_datetime_from_datetime(date_time):
    tz = pytz.timezone("Asia/Shanghai")
    return tz.localize(date_time)


def get_timezone_aware_datetime_from_date(date):
    return get_timezone_aware_datetime_from_datetime(datetime.datetime.combine(date, datetime.time(0)))


def get_timezone_aware_datetime_from_date_str(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return get_timezone_aware_datetime_from_date(date)


class BookableResource(models.Model):
    alias = models.CharField(max_length=256, null=True, blank=True)
    approver = models.ForeignKey(User)

    def get_title(self):
        """
        Used by calendar to get newly added resrouce title
        :return:
        """
        return self.alias

    def __unicode__(self):
        return unicode(self.alias)


class BookingRequestBase(models.Model):
    is_approved = models.BooleanField()
    is_ongoing = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    project = models.CharField(max_length=256)
    comments = models.CharField(max_length=256, null=True, blank=True, default="")

    def clean_fields(self, exclude=None):
        """
        Work around for date time field, the form for this field used date field
        :param exclude:
        :return:
        """
        self.start = str(get_timezone_aware_datetime_from_date(self.start))
        self.end = str(get_timezone_aware_datetime_from_date(self.end) + datetime.timedelta(days=1))
        return super(BookingRequestBase, self).clean_fields(exclude)

    def __unicode__(self):
        return unicode("%s: %s - %s" % (self.requester.username, str(self.start), str(self.end)))

    class Meta:
        abstract = True


class BookingRequest(BookingRequestBase):
    requester = models.ForeignKey(User)
    approver = models.ForeignKey(User, related_name="booking_request_approver", null=True, blank=True)
    resource = models.ForeignKey(BookableResource)

    def __unicode__(self):
        return unicode("%s: %s - %s" % (self.requester.username, str(self.start), str(self.end)))


import eav
eav.register(BookableResource)


from south.modelsinspector import add_ignored_fields
add_ignored_fields(["^eav\.fields\.EavDatatypeField"])
add_ignored_fields(["^eav\.fields\.EavSlugField"])