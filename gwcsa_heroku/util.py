from datetime import date, datetime
import re
import sys
import unicodedata

from django.db import connection

from gwcsa_heroku.constants import *
from gwcsa_heroku.models import *

def get_ascii(s):
    try:
        # if this works, the string only contains ascii characters
        return s.decode("ascii")
    except:
        pass

    try:
        # if possible, remove accents and print in base form
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore")
    except:
        return ""

def get_share_count(day):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT ROUND(SUM(CASE WHEN s.frequency = 'B' THEN s.quantity/2.0 ELSE quantity end), 1) AS total,
               s.content
          FROM gwcsa_heroku_share s,
               gwcsa_heroku_member m,
               gwcsa_heroku_season sn
         WHERE m.id = s.member_id
           AND m.season_id = sn.id
           AND sn.name = %s
           AND m.day = %s
      GROUP BY s.content
    """, [CURRENT_SEASON, day])
    r = {c: q for (q, c) in cursor.fetchall()}

    return [(desc, 0 if not code in r else r[code]) for code, desc in SHARES]

def get_ab_count_for_share(content):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT m.day,
               m.assigned_week,
               SUM(s.quantity) AS total
          FROM gwcsa_heroku_share s,
               gwcsa_heroku_member m,
               gwcsa_heroku_season sn
         WHERE m.id = s.member_id
           AND m.season_id = sn.id
           AND sn.name = %s
           AND s.frequency = 'B'
           AND s.content = %s
      GROUP BY m.day, m.assigned_week
      ORDER BY m.day, m.assigned_week
    """, [CURRENT_SEASON, content])

    results = []
    for day, assigned_week, total in cursor.fetchall():
        results.append((
            [desc for code, desc in DAYS if code == day][0],
            assigned_week,
            total
        ))

    return results

def get_weekly_count_for_shares():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT m.day,
               s.content,
               SUM(s.quantity) AS total
          FROM gwcsa_heroku_share s,
               gwcsa_heroku_member m,
               gwcsa_heroku_season sn
         WHERE m.id = s.member_id
           AND m.season_id = sn.id
           AND sn.name = %s
           AND s.frequency = 'W'
      GROUP BY m.day, s.content
      ORDER BY m.day, s.content desc
    """, [CURRENT_SEASON])

    results = []
    for day, content, total in cursor.fetchall():
        results.append((
            [desc for code, desc in DAYS if code == day][0],
            [desc for code, desc in SHARES if code == content][0],
            total
        ))

    return results

def get_distro_dates(day, week=None):
    if day == WEDNESDAY:
        if week == A_WEEK:
            return WED_A_DATES
        elif week == B_WEEK:
            return WED_B_DATES
        elif not week:
            return sorted(WED_A_DATES + WED_B_DATES)
        raise Exception("Invalid value for 'week' parameter: %s" % week)

    if day == SATURDAY:
        if week == A_WEEK:
            return SAT_A_DATES
        elif week == B_WEEK:
            return SAT_B_DATES
        elif not week:
            return sorted(SAT_A_DATES + SAT_B_DATES)
        raise Exception("Invalid value for 'week' parameter: %s" % week)

    raise Exception("Invalid value for 'day' parameter: %s" % day)

def distro_date_is_week(date, week):
    if type(date) is datetime:
        date = date.date()

    if week == A_WEEK:
        return date in (SAT_A_DATES + WED_A_DATES)
    if week == B_WEEK:
        return date in (SAT_B_DATES + WED_B_DATES)

    raise Exception("Invalid value for 'week' parameter: %s" % week)


# TODO: verify that column headers match expected title so that we're not
#       mis-processing columns (Farmigo changes the csv export regularly)
SIGNUP_DATE = 0
FIRST_NAME = 3
LAST_NAME = 2
EMAIL = 4
SHARE_DESCRIPTION = 5
SEASON = 6
PHONE = 8
SECONDARY_FIRST_NAME = 16
SECONDARY_LAST_NAME = 17
SECONDARY_EMAIL = 15
ROUTE = 19

# TODO: record last updated date to be displayed on page
def add_update_member_from_farmigo_csv_entry(line):
    # replace commas in values with semi-colons (subscription info esp.)
    for value in re.compile(',("[^"]+?,[^"]+?"),').findall(line):
        line = line.replace(value, re.sub(',', ';', value))
    d = [re.sub('"$', '', re.sub('^"', '', v)) for v in line.split(",")]

    # don't process member if not a current year member
    if CURRENT_SEASON not in d[SEASON]:
        return

    # update member
    member = Member.get_or_create_member(d[FIRST_NAME], d[LAST_NAME], d[EMAIL].lower())
    member.day = WEDNESDAY if "Wednesday" in d[ROUTE] else SATURDAY
    member.farmigo_signup_date = datetime.strptime(d[SIGNUP_DATE], "%m/%d/%Y %H:%M")
    member.farmigo_share_description = re.sub('"', '', re.sub(';', ',', d[SHARE_DESCRIPTION]))
    member.phone = re.sub("[-.()\s]", "", d[PHONE])
    if re.match("\d{10}", member.phone):
        member.phone = "%s-%s-%s" % (member.phone[0:3], member.phone[3:6], member.phone[6:])
    member.secondary_first_name = d[SECONDARY_FIRST_NAME]
    member.secondary_last_name = d[SECONDARY_LAST_NAME]
    member.secondary_email = d[SECONDARY_EMAIL]
    member.save()

    # re-create all member shares
    Share.objects.filter(member=member).delete()
    for s in member.farmigo_share_description.split(","):
        quantity = int(re.match("\d+", s.strip()).group(0))
        if re.compile("Biweekly Vegetable Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,VEGETABLES)
        elif re.compile("Weekly Vegetable Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,VEGETABLES)
        elif re.compile("Biweekly Vegeholic", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,2*quantity,BIWEEKLY,VEGETABLES)
        elif re.compile("Weekly Vegeholic", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,2*quantity,WEEKLY,VEGETABLES)
        elif re.compile("Biweekly Fruit Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,FRUIT)
        elif re.compile("Weekly Fruit Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,FRUIT)
        elif re.compile("Biweekly Egg Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,EGGS)
        elif re.compile("Weekly Egg Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,EGGS)
        elif re.compile("Biweekly Flower share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,FLOWERS)
        elif re.compile("Weekly Flower Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,FLOWERS)
        elif re.compile("Biweekly Mega Combo", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,VEGETABLES)
            Share.add_or_create_share(member,quantity,BIWEEKLY,FRUIT)
            Share.add_or_create_share(member,quantity,BIWEEKLY,EGGS)
            Share.add_or_create_share(member,quantity,BIWEEKLY,FLOWERS)
        elif re.compile("Weekly Mega Combo", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,VEGETABLES)
            Share.add_or_create_share(member,quantity,WEEKLY,FRUIT)
            Share.add_or_create_share(member,quantity,WEEKLY,EGGS)
            Share.add_or_create_share(member,quantity,WEEKLY,FLOWERS)
        elif re.compile("Veg PLANT Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,PLANTS)
        elif re.compile("Cheese Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,CHEESE)
        elif re.compile("Meat Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,MEAT)
        elif re.compile("Pickles", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,PICKLES_AND_PRESERVES)


