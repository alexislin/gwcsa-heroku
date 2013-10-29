from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

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
    year = models.CharField(max_length=6,null=False,choices=SEASONS,default=CURRENT_SEASON)

class WorkShift(TimestampedModel):
    season = models.ForeignKey(Season,null=False)
    day = models.CharField(max_length=2,choices=DAYS,null=False)
    name = models.CharField(max_length=60,null=False)
    location = models.CharField(max_length=120,null=False)
    location2 = models.CharField(max_length=120,null=False,default='')
    num_required_per_member = models.PositiveIntegerField(null=False)

class WorkShiftDateTime(TimestampedModel):
    shift = models.ForeignKey(WorkShift,null=False)
    date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    num_members_required = models.PositiveIntegerField(null=False)

class Member(TimestampedModel):
    WEEK = (
        ('A', 'A Week'),
        ('B', 'B Week'),
        ('W', 'Weekly'),
    )

    season = models.ForeignKey(Season,null=False)
    first_name = models.CharField(max_length=100,null=False)
    last_name = models.CharField(max_length=100,null=False)
    email = models.EmailField(max_length=254,null=False)
    phone = models.CharField(max_length=20,null=False,default='')
    day = models.CharField(max_length=2,choices=DAYS)
    farmigo_signup_date = models.DateTimeField()
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

class MemberWorkShift(TimestampedModel):
    member = models.ForeignKey(Member,null=False)
    workshift_date_time = models.ForeignKey(WorkShiftDateTime,null=False)
