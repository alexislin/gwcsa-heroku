from django.db import models

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
        return [s.date for s in WorkShiftDateTime.objects.filter(shift=self) if not s.is_full()]

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

    def is_full(self):
        n = WorkShiftDateTime.objects.filter(shift=self.shift) \
            .filter(start_time=self.start_time).filter(date=self.date).count()
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
    farmigo_share_description = models.TextField(null=False,default='')
    is_weekly = models.BooleanField(null=False,default=False)
    is_biweekly = models.BooleanField(null=False,default=False)
    assigned_week = models.CharField(max_length=1,choices=WEEK)

    secondary_first_name = models.CharField(max_length=100,null=False)
    secondary_last_name = models.CharField(max_length=100,null=False)
    secondary_email = models.EmailField(max_length=254,null=False)

    def get_name(self):
        return self.first_name + " " + self.last_name
    name = property(get_name)

    def get_formatted_signup_date(self):
        if not self.farmigo_signup_date:
            return ""
        return self.farmigo_signup_date.strftime("%m/%d/%Y %H:%M")
    formatted_signup_date = property(get_formatted_signup_date)

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
