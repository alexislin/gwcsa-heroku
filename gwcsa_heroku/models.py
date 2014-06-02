import sys

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save

from gwcsa_heroku.constants import *

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        abstract = True

DAYS = (
    ('W', 'Wednesday'),
    ('S', 'Saturday'),
)
WEDNESDAY = DAYS[0][0]
SATURDAY = DAYS[1][0]

SEASONS = (
    ('2014', '2014'),
)
CURRENT_SEASON = SEASONS[0][0]

class Season(TimestampedModel):
    name = models.CharField(max_length=6,null=False,choices=SEASONS,default=CURRENT_SEASON)

class WorkShift(TimestampedModel):
    season = models.ForeignKey(Season,null=False)
    day = models.CharField(max_length=2,choices=DAYS,null=False)
    name = models.CharField(max_length=60,null=False)
    location = models.CharField(max_length=120,null=False)
    location2 = models.CharField(max_length=120,null=False,default='')
    note = models.CharField(max_length=200,null=False,default='')
    num_required_per_member = models.PositiveIntegerField(null=False)

# TODO: filter out the first two weeks of distro shifts
    def get_available_dates(self):
        dates = [s.date for s in WorkShiftDateTime.objects.filter(shift=self) \
            if not s.is_full()]
        return sorted(list(set(dates)))

    def get_available_dates_for_member(self, member):
        dates = self.get_available_dates()
        dates.extend([ms.workshift_date_time.date for ms in \
            MemberWorkShift.objects.filter(workshift_date_time__shift=self).filter(member=member)])
        return sorted(dates)


class WorkShiftDateTime(TimestampedModel):
    shift = models.ForeignKey(WorkShift,null=False)
    date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    num_members_required = models.PositiveIntegerField(null=False)

    def get_week(self):
        if self.date in WED_A_DATES or self.date in SAT_A_DATES:
            return A_WEEK
        elif self.date in WED_B_DATES or self.date in SAT_B_DATES:
            return B_WEEK
        else:
            raise Exception("Could not determine A/B week for date: %s" % self.date)
    week = property(get_week)

    def is_full(self):
        n = MemberWorkShift.objects.filter(workshift_date_time=self).count()
        return n >= self.num_members_required

WEEK = (
    ('A', 'A Week'),
    ('B', 'B Week'),
    ('W', 'Weekly'),
)
A_WEEK = WEEK[0][0]
B_WEEK = WEEK[1][0]

class Member(TimestampedModel):
    season = models.ForeignKey(Season,null=False)
    first_name = models.CharField(max_length=100,null=False)
    last_name = models.CharField(max_length=100,null=False)
    email = models.EmailField(max_length=254,null=False)
    phone = models.CharField(max_length=20,null=False,default='')
    day = models.CharField(max_length=2,choices=DAYS)
    farmigo_signup_date = models.DateTimeField(null=True)
    farmigo_last_modified_date = models.DateTimeField(null=True)
    farmigo_share_description = models.TextField(null=False,default='')
    assigned_week = models.CharField(max_length=1,choices=WEEK,null=True)

    secondary_first_name = models.CharField(max_length=100,null=False)
    secondary_last_name = models.CharField(max_length=100,null=False)
    secondary_email = models.EmailField(max_length=254,null=False)

    is_weekly = models.BooleanField()
    has_biweekly = models.BooleanField()

    def get_name(self):
        return self.first_name + " " + self.last_name
    name = property(get_name)

    def get_secondary_name(self):
        return self.secondary_first_name + " " + self.secondary_last_name
    secondary_name = property(get_secondary_name)

    def get_formatted_signup_date(self):
        if not self.farmigo_signup_date:
            return ""
        return self.farmigo_signup_date.strftime("%m/%d/%Y %H:%M")
    formatted_signup_date = property(get_formatted_signup_date)

    def get_workshift_week(self):
        weeks = [s.week for s in MemberWorkShift.objects.filter(member=self)]
        return weeks[0] if len(set(weeks)) == 1 else None
    workshift_week = property(get_workshift_week)

    def get_has_shifts(self):
        return MemberWorkShift.objects.filter(member=self).count() > 0
    has_shifts = property(get_has_shifts)

    def add_share_attributes(self):
        setattr(self, "a_week", False)

        d = { VEGETABLES: 0, FRUIT: 0, EGGS: 0, FLOWERS: 0 }
        for s in Share.objects.filter(member=self):
            if s.frequency == BIWEEKLY:
                d[s.content] += s.quantity
            if s.content in [MEAT, CHEESE, PICKLES_AND_PRESERVES] and s.quantity > 0:
                setattr(self, "a_week", True)

        # if this member has any weekly shares, then they're coming every week
        # anyway... don't need to force an A Week assignment
        if self.is_weekly:
            setattr(self, "a_week", False)

        setattr(self, "biweekly_share_counts",
            (d[VEGETABLES], d[FRUIT], d[EGGS], d[FLOWERS]))

    @staticmethod
    def get_or_create_member(first_name, last_name, email):
        if not first_name or not last_name or not email:
            raise Exception("Must provide first name, last name and email.")

        # always use lowercase only for emails
        email = email.lower()

        try:
            member = Member.objects.get(season=Season.objects.get(name=CURRENT_SEASON),email=email)

            if not first_name.lower() == member.first_name.lower() or \
                not last_name.lower() == member.last_name.lower():
                raise Exception(
                    "The email address '%s' is already in use by %s %s." % \
                    (email, member.first_name, member.last_name))

            return member

        except Member.DoesNotExist:
            member = Member.objects.create(
                season=Season.objects.get(name=CURRENT_SEASON),
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            return member

class MemberWorkShift(TimestampedModel):
    member = models.ForeignKey(Member,null=False)
    workshift_date_time = models.ForeignKey(WorkShiftDateTime,null=False)

    def get_week(self):
        return self.workshift_date_time.week
    week = property(get_week)

    def get_date(self):
        return self.workshift_date_time.date
    date = property(get_date)

    def __str__(self):
        return "Shift: %s | Date: %s | Day: %s | Time: %s - %s | Location: %s %s" % (
            self.workshift_date_time.shift.name,
            self.date.strftime("%-m/%-d/%Y"),
            self.workshift_date_time.shift.get_day_display(),
            self.workshift_date_time.start_time.strftime("%-I:%M %p"),
            self.workshift_date_time.end_time.strftime("%-I:%M %p"),
            self.workshift_date_time.shift.location,
            self.workshift_date_time.shift.location2
        )

SHARES = (
    ('V', 'Vegetables'),
    ('FR', 'Fruit'),
    ('E', 'Eggs'),
    ('FL', 'Flowers'),
    ('M', 'Meat'),
    ('C', 'Cheese'),
    ('PP', 'Pickles & Preserves'),
    ('P', 'Plants'),
)
VEGETABLES = SHARES[0][0]
FRUIT = SHARES[1][0]
EGGS = SHARES[2][0]
FLOWERS = SHARES[3][0]
MEAT = SHARES[4][0]
CHEESE = SHARES[5][0]
PICKLES_AND_PRESERVES = SHARES[6][0]
PLANTS = SHARES[7][0]

FREQUENCY = (
    ('B', 'Biweekly'),
    ('W', 'Weekly'),
    ('N', 'Not Applicable'),
)
BIWEEKLY = FREQUENCY[0][0]
WEEKLY = FREQUENCY[1][0]
NOT_APPLICABLE = FREQUENCY[2][0]

class Share(TimestampedModel):
    member = models.ForeignKey(Member,null=False)
    content = models.CharField(max_length=2,choices=SHARES,null=False)
    quantity = models.PositiveIntegerField(null=False)
    frequency = models.CharField(max_length=1,choices=FREQUENCY,null=False)

    @staticmethod
    def add_or_create_share(member, quantity, frequency, content):
        try:
            share = Share.objects.get(member=member,content=content,frequency=frequency)
            share.quantity += quantity
            share.save()
        except Share.DoesNotExist:
            Share.objects.create(member=member,content=content,frequency=frequency,quantity=quantity)

class EmailLog(TimestampedModel):
    member = models.ForeignKey(Member,null=True)
    to_email = models.EmailField(max_length=254,null=False)
    to_name = models.CharField(max_length=210,null=False)
    subject = models.CharField(max_length=350,null=False)
    status_code = models.CharField(max_length=10,null=False)

def log_ab_week_assignment(sender, **kwargs):
    member = kwargs["instance"]
    WeekAssignmentLog.objects.create(
        member=member,assigned_week=member.assigned_week,module_name=__name__)

post_save.connect(log_ab_week_assignment, sender=Member)

class WeekAssignmentLog(TimestampedModel):
    member = models.ForeignKey(Member,null=False)
    assigned_week = models.CharField(max_length=1,choices=WEEK,null=True)
    # TODO: remove the module_name - this isn't useful anymore now
    # that we're using signals
    module_name = models.CharField(max_length=50, null=False)

