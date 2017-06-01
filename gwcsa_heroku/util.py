from datetime import date, datetime
import logging
import re
import sys
import unicodedata

from django.db import connection

from gwcsa_heroku.models import *

logger = logging.getLogger(__name__)

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

def get_share_list(content, day, week):
    cursor = connection.cursor()
    cursor.execute("""
        select m.id,
               sum(s.quantity)
          from gwcsa_heroku_member m,
               gwcsa_heroku_share s,
               gwcsa_heroku_season sn
         where m.season_id = sn.id
           and sn.name = %s
           and m.id = s.member_id
           and s.content = %s
           and m.day = %s
           and (s.frequency in ('W', 'N') or m.assigned_week = %s)
      group by m.id
      order by m.first_name, m.last_name
    """, [CURRENT_SEASON, content, day, week])
    return cursor.fetchall()

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

    return [0 if not VEGETABLES in r else r[VEGETABLES], \
        0 if not FRUIT in r else r[FRUIT], \
        0 if not EGGS in r else r[EGGS], \
        0 if not FLOWERS in r else r[FLOWERS], \
        0 if not PERSONAL_SIZE in r else r[PERSONAL_SIZE], \
        0 if not VEGETABLES_SUMMER_ONLY in r else r[VEGETABLES_SUMMER_ONLY], \
        0 if not BEER in r else r[BEER], \
        0 if not CHEESE in r else r[CHEESE], \
        0 if not MEAT in r else r[MEAT], \
        0 if not BREAD in r else r[BREAD], \
        0 if not PLANTS in r else r[PLANTS]]

def get_ab_count_for_location(loc):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT s.content,
               s.frequency,
               m.assigned_week,
               SUM(s.quantity) AS total
          FROM gwcsa_heroku_share s,
               gwcsa_heroku_member m,
               gwcsa_heroku_season sn
         WHERE m.id = s.member_id
           AND m.season_id = sn.id
           AND sn.name = %s
           AND (s.frequency = %s or s.frequency = %s)
           AND m.day = %s
      GROUP BY s.content, s.frequency, m.assigned_week
      ORDER BY s.content, s.frequency, m.assigned_week
    """, [CURRENT_SEASON, BIWEEKLY, WEEKLY, loc])
    r = {}
    for c, f, aw, t in cursor.fetchall():
        # check for unexpected situations
        if c != BEER and f == WEEKLY and aw not in (WEEKLY_PLUS_A, WEEKLY_PLUS_B, WEEKLY, None):
            raise Exception(("Location '{0}' has member with weekly {1} share, "
                "and member is assigned to '{3}'").format(loc, c, f, aw))
        if f == BIWEEKLY and aw == WEEKLY:
            raise Exception(("Location '{0}' has a weekly member with a "
                "biweekly {1} share").format(loc, c))

        if f == BIWEEKLY:
            if not c in r:
                r[c] = {aw: t}
            else:
                r[c][aw] = t
        elif f == WEEKLY:
            if not c in r:
                r[c] = {WEEKLY: t}
            else:
                if not WEEKLY in r[c]:
                    r[c][WEEKLY] = t
                else:
                    r[c][WEEKLY] += t
        else:
            raise Exception("unexpected value for f: '{0}'".format(f))

    results = []
    for share in [VEGETABLES, FRUIT, EGGS, FLOWERS]:
        cnts = [share]
        if not share in r:
            cnts.extend([0] * 4)
        else:
            for week in [A_WEEK, WEEKLY_PLUS_A, B_WEEK, WEEKLY_PLUS_B, None, WEEKLY]:
                cnts.append(0 if not week in r[share] else r[share][week])
        results.append(cnts)
    logger.debug("results: %s" % results)
    return results


# TODO: verify that column headers match expected title so that we're not
#       mis-processing columns (Farmigo changes the csv export regularly)
LAST_MODIFIED_DATE = 0
SIGNUP_DATE = 1
FIRST_NAME = 3
LAST_NAME = 2
EMAIL = 4
SHARE_DESCRIPTION = 5
SEASON = 6
LOCATION = 7
PHONE = 8
SECONDARY_FIRST_NAME = 16
SECONDARY_LAST_NAME = 17
SECONDARY_EMAIL = 15

# TODO: record last updated date to be displayed on page
def add_update_member_from_farmigo_csv_entry(line):
    # replace commas in values with semi-colons (subscription info esp.)
    for value in re.compile(',("[^"]+?,[^"]+?"),').findall(line):
        line = line.replace(value, re.sub(',', ';', value))
    d = [re.sub('"$', '', re.sub('^"', '', v)) for v in line.split(",")]

    # don't process member if not a current year member
    if len(d) < SEASON or CURRENT_SEASON not in d[SEASON]:
        return
    logger.debug("getting/creating member '%s' '%s' '%s'" % (d[FIRST_NAME], d[LAST_NAME], d[EMAIL]))
    member = Member.get_or_create_member(d[FIRST_NAME], d[LAST_NAME], d[EMAIL].lower())

    # don't update member if their farmigo subscription hasn't been modified
    last_modified_date = datetime.strptime(d[LAST_MODIFIED_DATE], "%Y/%m/%d %H:%M:%S")
    if member.farmigo_last_modified_date == last_modified_date:
        return

    # update member
    loc = d[LOCATION].lower()
    if "brooklyn heights" in loc: member.day = BROOKLYN_HEIGHTS
    elif "bayport" in loc: member.day = BAYPORT
    elif "bay ridge" in loc: member.day = BAYRIDGE
    elif "bed stuy" in loc: member.day = BED_STUY
    elif "bushwick" in loc: member.day = BUSHWICK
    elif "carroll gardens" in loc: member.day = CARROLL_GARDENS
    elif "forest hills" in loc: member.day = FOREST_HILLS
    elif "glendale" in loc: member.day = GLENDALE
    elif "greenpoint" in loc: member.day = GREENPOINT
    elif "kew gardens" in loc: member.day = KEW_GARDENS
    elif "kensington" in loc and "wed" in loc: member.day = KENSINGTON_WED
    elif "kensington" in loc and "sat" in loc: member.day = KENSINGTON_SAT
    elif "mt sinai" in loc: member.day = MT_SINAI
    elif "riverhead" in loc and "wed" in loc: member.day = RIVERHEAD_WED
    elif "roslyn" in loc: member.day = ROSLYN
    elif "riverhead" in loc and "sat" in loc: member.day = RIVERHEAD_SAT
    elif "ridgewood" in loc: member.day = RIDGEWOOD
    elif "stony brook" in loc: member.day = STONY_BROOK
    elif "uws" in loc: member.day = UWS
    elif "williamsburg" in loc: member.day = WILLIAMSBURG
    elif "westhampton" in loc: member.day = WESTHAMPTON_BEACH
    else: raise Exception("Unknown location: %s" % d[LOCATION])

    member.farmigo_signup_date = datetime.strptime(d[SIGNUP_DATE], "%Y-%m-%d")
    member.farmigo_last_modified_date = datetime.strptime(d[LAST_MODIFIED_DATE], "%Y/%m/%d %H:%M:%S")
    member.farmigo_share_description = re.sub('"', '', re.sub(';', ',', d[SHARE_DESCRIPTION]))
    member.farmigo_share_description = re.sub('\(Veg,Fru?i?t,Flr,Eggs\)', '', member.farmigo_share_description)
    member.phone = re.sub("[-.()\s]", "", d[PHONE])
    if re.match("\d{10}", member.phone):
        member.phone = "%s-%s-%s" % (member.phone[0:3], member.phone[3:6], member.phone[6:])
    member.save()

    logger.debug("share description: %s" % member.farmigo_share_description)
    # re-create all member shares
    Share.objects.filter(member=member).delete()
    for s in member.farmigo_share_description.split(","):
        logger.debug("s=%s" % s)
        quantity = int(re.match("\d+", s.strip()).group(0))
        if re.compile("Vegetable Biweekly Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,VEGETABLES)
        elif re.compile("Vegetable Weekly Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,VEGETABLES)
        elif re.compile("Vegeholic Biweekly Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,2*quantity,BIWEEKLY,VEGETABLES)
        elif re.compile("Vegeholic Weekly Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,2*quantity,WEEKLY,VEGETABLES)
        elif re.compile("Fruit Share Biweekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,FRUIT)
        elif re.compile("Fruit Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,FRUIT)
        elif re.compile("Egg Share biweekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,EGGS)
        elif re.compile("Egg Share Weekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,EGGS)
        elif re.compile("Sunflower Share Biweekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,FLOWERS)
        elif re.compile("Sunflower Share Weekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,FLOWERS)
        elif re.compile("COMBO Biweekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,BIWEEKLY,VEGETABLES)
            Share.add_or_create_share(member,quantity,BIWEEKLY,FRUIT)
            Share.add_or_create_share(member,quantity,BIWEEKLY,EGGS)
            Share.add_or_create_share(member,quantity,BIWEEKLY,FLOWERS)
        elif re.compile("COMBO Weekly", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,VEGETABLES)
            Share.add_or_create_share(member,quantity,WEEKLY,FRUIT)
            Share.add_or_create_share(member,quantity,WEEKLY,EGGS)
            Share.add_or_create_share(member,quantity,WEEKLY,FLOWERS)
        elif re.compile("Personal Size Weekly Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,PERSONAL_SIZE)
        elif re.compile("Craft Beer", re.IGNORECASE).search(s):
            # marked as a WEEKLY share because Eve is allowing people to
            # buy beer without any other shares (not even veggies)
            Share.add_or_create_share(member,quantity,WEEKLY,BEER)
        elif re.compile("PLANT Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,PLANTS)
        elif re.compile("Cheese Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,CHEESE)
        elif re.compile("Meat Share", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,MEAT)
        elif re.compile("Bread", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,NOT_APPLICABLE,BREAD)
        elif re.compile("Vegetable Share - SUMMER ONLY", re.IGNORECASE).search(s):
            Share.add_or_create_share(member,quantity,WEEKLY,VEGETABLES_SUMMER_ONLY)
        elif re.compile("Low Income Fund Donation", re.IGNORECASE).search(s):
            pass
        else:
            raise Exception("Unknown share type: %s" % s)

    member.is_weekly = Share.objects.filter(
            member=member,frequency=WEEKLY
        ).exclude(content=BEER).count() > 0
    member.has_biweekly = Share.objects.filter(
            member=member,frequency=BIWEEKLY
        ).count() > 0
    member.save()

