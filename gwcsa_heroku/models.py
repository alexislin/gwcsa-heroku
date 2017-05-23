import logging
import sys

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save

logger = logging.getLogger(__name__)

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        abstract = True

DAYS = (
    ('W', 'Wednesday'), #deprecated
    ('S', 'Saturday'), #deprecated
    ('BH', 'Brooklyn Heights Sweet Pea CSA, Brooklyn - Wednesday'),
    ('BP', 'Bayport, Long Island - Wednesday'),
    ('BR', 'Bayridge/Yellow Hook, Brooklyn - Wednesday'),
    ('BS', 'Bed Stuy, Brooklyn - Saturday'),
    ('BW', 'Bushwick, Brooklyn - Wednesday'),
    ('CG', 'Carroll Gardens, Brookyn - Saturday'),
    ('FH', 'Forest Hills Farmers Market, Queens - Sunday'),
    ('GD', 'Glendale, Queens - Saturday'),
    ('GP', 'Greenpoint, Brooklyn - Wednesday'),
    ('KG', 'Kew Gardens, Queens - Sunday'),
    ('KW', 'Kensington/Windsor Terrace, Brooklyn - Saturday'),
    ('MS', 'Mt Sinai, Long Island - Wednesday'),
    ('RH', 'Riverhead Farm, Long Island - Wednesday'),
    ('RN', 'Roslyn/East Hills, Long Island - Wednesday'),
    ('RS', 'Riverhead Farm, Long Island - Saturday'),
    ('RW', 'Ridgewood, Queens - Saturday'),
    ('SB', 'Stony Brook/Avalon Park, Long Island - Wednesday'),
    ('UW', 'UWS: Ansche Chesed, Manhattan - Wednesday'),
    ('WB', 'Williamsburg-McCarren Park, Brooklyn - Saturday'),
    ('WH', 'Westhampton Beach Farmers Market, Long Island - Saturday'),
)
WEDNESDAY = DAYS[0][0]
SATURDAY = DAYS[1][0]
BROOKLYN_HEIGHTS = DAYS[2][0]
BAYPORT = DAYS[3][0]
BAYRIDGE = DAYS[4][0]
BED_STUY = DAYS[5][0]
BUSHWICK = DAYS[6][0]
CARROLL_GARDENS = DAYS[7][0]
FOREST_HILLS = DAYS[8][0]
GLENDALE = DAYS[9][0]
GREENPOINT = DAYS[10][0]
KEW_GARDENS = DAYS[11][0]
KENSINGTON = DAYS[12][0]
MT_SINAI = DAYS[13][0]
RIVERHEAD_WED = DAYS[14][0]
ROSLYN = DAYS[15][0]
RIVERHEAD_SAT = DAYS[16][0]
RIDGEWOOD = DAYS[17][0]
STONY_BROOK = DAYS[18][0]
UWS = DAYS[19][0]
WILLIAMSBURG = DAYS[20][0]
WESTHAMPTON_BEACH = DAYS[21][0]

SEASONS = (
    ('2014', '2014'),
    ('2015', '2015'),
    ('2016', '2016'),
    ('2017', '2017'),
)
CURRENT_SEASON = SEASONS[3][0]

class Season(TimestampedModel):
    name = models.CharField(max_length=6,null=False,choices=SEASONS,default=CURRENT_SEASON)

WEEK = (
    ('A', 'A'),
    ('B', 'B'),
    ('X', 'AB/A'),
    ('Y', 'AB/B'),
    ('W', 'AB'),
)
A_WEEK = WEEK[0][0]
B_WEEK = WEEK[1][0]
WEEKLY_PLUS_A = WEEK[2][0]
WEEKLY_PLUS_B = WEEK[3][0]
WEEKLY = WEEK[4][0]

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

    # returns a simplified representation of assigned_week
    # 'A' and 'AB/A' return as 'A'
    # 'B' and 'AB/B' return as 'B'
    def get_assigned_week_simplified(self):
        if self.assigned_week in (A_WEEK, WEEKLY_PLUS_A):
            return A_WEEK
        elif self.assigned_week in (B_WEEK, WEEKLY_PLUS_B):
            return B_WEEK
        elif self.assigned_week == WEEKLY or self.assigned_week is None:
            return self.assigned_week
        else:
            raise Exception("This logic needs to be updated.")
    assigned_week_simplified = property(get_assigned_week_simplified)

    # returns the long version of the week assignment (for display/export)
    def get_assigned_week_description(self):
        if self.assigned_week is None:
            return "TBD"
        for code, desc in WEEK:
            if self.assigned_week == code:
                return desc
        raise Exception("Didn't find description for WEEK code '%s'" % self.assigned_week)
    assigned_week_description = property(get_assigned_week_description)

    # ensures that assigned_week is set correctly. This encapsulates
    # logic that we don't want to repeat all over.
    def set_assigned_week(self, value):
        if value in (A_WEEK, WEEKLY_PLUS_A):
            self.assigned_week = A_WEEK if not self.is_weekly else WEEKLY_PLUS_A
        elif value in (B_WEEK, WEEKLY_PLUS_B):
            self.assigned_week = B_WEEK if not self.is_weekly else WEEKLY_PLUS_B
        elif value == WEEKLY:
            if self.has_biweekly:
                raise Exception("Cannot assign 'W' to a member with biweekly shares.id=%s" % self.id)
            if not self.is_weekly:
                raise Exception("Cannot assign 'W' to a member without weekly shares. id=%s" % self.id)
            self.assigned_week = WEEKLY
        elif value is None:
            self.assigned_week = None
        else:
            raise Exception("Unknown value for week assignment: %s" % value)
        self.save()

    def get_name(self):
        return self.first_name + " " + self.last_name
    name = property(get_name)

    def get_secondary_name(self):
        return self.secondary_first_name + " " + self.secondary_last_name
    secondary_name = property(get_secondary_name)

    def get_formatted_signup_date(self):
        if not self.farmigo_signup_date:
            return ""
        return self.farmigo_signup_date.strftime("%m/%d/%Y")
    formatted_signup_date = property(get_formatted_signup_date)

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

    def get_export_row(self):
        indices = { VEGETABLES: 0, FRUIT: 3, EGGS: 6, FLOWERS: 9,
            VEGETABLES_SUMMER_ONLY: 12, PERSONAL_SIZE: 13,
            BEER: 14, CHEESE: 15, MEAT: 16, BREAD: 17 }
        # V(A), V(B), V(?), FR(A), FR(B), FR(?),  0- 5
        # E(A), E(B), E(?), FL(A), FL(B), FL(?),  6-11
        # Vso, PS, BR, C, M, BD                  12-17
        d = [0]*18
        for s in Share.objects.filter(member=self):
            if s.content in (VEGETABLES, FRUIT, EGGS, FLOWERS):
                i = indices[s.content]
                if s.frequency == WEEKLY:
                    d[i] += s.quantity
                    d[i+1] += s.quantity
                elif s.frequency == BIWEEKLY:
                    week = self.get_assigned_week_simplified()
                    if week == A_WEEK:
                        d[i] += s.quantity
                    elif week == B_WEEK:
                        d[i+1] += s.quantity
                    elif not week:
                        d[i+2] += s.quantity
                    else:
                        raise Exception("weekly member with biweekly shares! id={0}".format(self.id))
            elif s.content in (VEGETABLES_SUMMER_ONLY, PERSONAL_SIZE, BEER, CHEESE, MEAT, BREAD):
                d[indices[s.content]] += s.quantity

        return [self.first_name, self.last_name, self.get_formatted_signup_date(),\
                self.email, self.phone, self.get_assigned_week_description()] \
            + d + [self.farmigo_share_description]

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

SHARES = (
    ('V', 'Vegetables'),
    ('FR', 'Fruit'),
    ('E', 'Eggs'),
    ('FL', 'Flowers'),
    ('M', 'Meat'),
    ('C', 'Cheese'),
    ('PP', 'Pickles & Preserves'), #deprecated
    ('P', 'Plants'),
    ('B', 'Bread'),
    ('BR', 'Beer'),
    ('PS', 'Personal Size'),
    ('VS', 'Vegetables - Summer Only'),
)
VEGETABLES = SHARES[0][0]
FRUIT = SHARES[1][0]
EGGS = SHARES[2][0]
FLOWERS = SHARES[3][0]
MEAT = SHARES[4][0]
CHEESE = SHARES[5][0]
PICKLES_AND_PRESERVES = SHARES[6][0]
PLANTS = SHARES[7][0]
BREAD = SHARES[8][0]
BEER = SHARES[9][0]
PERSONAL_SIZE = SHARES[10][0]
VEGETABLES_SUMMER_ONLY = SHARES[11][0]

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

    m = Member.objects.filter(id=member.id)
    if len(m) > 0 and member.assigned_week <> m[0].assigned_week:
        WeekAssignmentLog.objects.create(member=member,assigned_week=member.assigned_week,module_name=__name__)
    pass

pre_save.connect(log_ab_week_assignment, sender=Member)

class WeekAssignmentLog(TimestampedModel):
    member = models.ForeignKey(Member,null=False)
    assigned_week = models.CharField(max_length=1,choices=WEEK,null=True)
    # TODO: remove the module_name - this isn't useful anymore now
    # that we're using signals
    module_name = models.CharField(max_length=50, null=False)

