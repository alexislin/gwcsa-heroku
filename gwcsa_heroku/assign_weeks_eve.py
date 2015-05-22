#!/usr/bin/env python
from sets import Set
import re

''' THIS IS INTENDED TO BE RUN AS A CMD LINE SCRIPT '''

class Member:
    def __init__(self, email, location):
        self.email = email.lower()
        self.location = location
        self.share_description = ""
        self.mandatory_a_week = False
        self.veggies = 0
        self.fruit = 0
        self.eggs = 0
        self.flowers = 0
        self.biweekly = True
        self.assigned_week = "unassigned"

    def __str__(self):
        if not self.biweekly:
            return "\n".join(("WEEKLY [%s] %s" % (self.email, self.share_description), ""))

        return "\n".join(("%s [%s]" % (self.email, self.location),
            self.share_description,
            "veggies: %s, fruit: %s, eggs: %s, flowers: %s" % \
                (self.veggies, self.fruit, self.eggs, self.flowers),
            "biweekly: %s [%s], a_week: %s" % \
                (self.biweekly, self.assigned_week, self.mandatory_a_week),
            ""))


EMAIL = 4
SHARE_DESCRIPTION = 5
SEASON = 6
LOCATION = 7
ROUTE = 19

def get_member_from_farmigo_csv_entry(line):
    # replace commas in values with semi-colons (subscription info esp.)
    for value in re.compile(',("[^"]+?,[^"]+?"),').findall(line):
        line = line.replace(value, re.sub(',', ';', value))
    d = [re.sub('"$', '', re.sub('^"', '', v)) for v in line.split(",")]

    # some lines are just hanging remnants of member info, broken by the
    # comments column
    if len(d) < LOCATION or d[SEASON] <> "Summer 2015":
        member = Member(line, "BOGUS")
        member.biweekly = False
        return member

    member = Member(d[EMAIL], d[LOCATION])
    member.share_description = re.sub('"', '', re.sub(';', ',', d[SHARE_DESCRIPTION]))

    share_description = re.sub("\(.*?\)", "", member.share_description)

    for s in share_description.split(","):
        quantity = int(re.match("\d+", s.strip()).group(0))
        if re.compile("Vegetable Biweekly Share", re.IGNORECASE).search(s):
            member.veggies += quantity
        elif re.compile("Vegeholic Biweekly", re.IGNORECASE).search(s):
            member.veggies += 2*quantity
        elif re.compile("Fruit Share Biweekly", re.IGNORECASE).search(s):
            member.fruit += quantity
        elif re.compile("Egg Share biweekly", re.IGNORECASE).search(s):
            member.eggs += quantity
        elif re.compile("Flower share biweekly", re.IGNORECASE).search(s):
            member.flowers += quantity
        elif re.compile("COMBO Biweekly", re.IGNORECASE).search(s):
            member.veggies += quantity
            member.fruit += quantity
            member.eggs += quantity
            member.flowers += quantity
        elif re.compile("Vegetable Weekly Share", re.IGNORECASE).search(s) or \
             re.compile("Vegeholic Weekly Share", re.IGNORECASE).search(s) or \
             re.compile("Fruit Share - NOT", re.IGNORECASE).search(s) or \
             re.compile("Egg Share Weekly", re.IGNORECASE).search(s) or \
             re.compile("Flower Share Weekly", re.IGNORECASE).search(s) or \
             re.compile("COMBO weekly", re.IGNORECASE).search(s):
            member.biweekly = False
            member.assigned_week = "N/A"
        elif re.compile("Cheese Share", re.IGNORECASE).search(s) or \
             re.compile("Meat Share", re.IGNORECASE).search(s) or \
             re.compile("Pickles", re.IGNORECASE).search(s) or \
             re.compile("Bread Share", re.IGNORECASE).search(s):
            member.mandatory_a_week = True
        elif re.compile("PLANT Share", re.IGNORECASE).search(s) or \
             re.compile("Low Income Fund", re.IGNORECASE).search(s) or \
             re.compile("Market Share", re.IGNORECASE).search(s):
            pass
        else:
            print member.share_description

    return member


def get_total(members, member=None):
    total = [0]*4
    for m in members:
        total = get_tplus([m.veggies, m.fruit, m.eggs, m.flowers], total)

    return total if not member else \
        get_tplus([member.veggies, member.fruit, member.eggs, member.flowers], total)

def get_tplus(t, s):
    return [sum(c) for c in zip(*(t, s))]

def get_tminus(t, s):
    return [x - y for x, y in zip(*(t, s))]

def get_diff(t1, t2):
    return sum([abs(x-y) for x, y in zip(*(t1, t2))])


#####################################
#####################################

with open("EveSubscriptions20150522.csv") as f:
    content = f.readlines()

locations = Set([])
members = []
for line in content[1:]:
    member = get_member_from_farmigo_csv_entry(line)
    locations.add(member.location)
    members.append(member)

# now assign A/B for all members of a given location
for location in locations:
    location_members = [m for m in members if m.location == location and m.biweekly]

    # assign A/B weeks
    if len(location_members) > 0:
        a_week = [m for m in location_members if m.mandatory_a_week]
        b_week = []

        # assign the rest of the members
        for m in [m for m in location_members if not m.mandatory_a_week]:
            diff_a = get_diff(get_total(a_week, m), get_total(b_week))
            diff_b = get_diff(get_total(a_week), get_total(b_week, m))
            if diff_a <= diff_b:
                a_week.append(m)
                m.assigned_week = "A"
            else:
                b_week.append(m)
                m.assigned_week = "B"

        print "----------------------------------------------------------------------"
        print "%s [%s biweekly members]" % (location, len(location_members))
        print "A WEEK TOTAL - Veggies: %s, Fruit: %s, Eggs: %s, Flowers: %s" % tuple(get_total(a_week))
        print "B WEEK TOTAL - Veggies: %s, Fruit: %s, Eggs: %s, Flowers: %s" % tuple(get_total(b_week))
        print ""
        print "A WEEK"
        for m in a_week:
            print "%s => %s" % (m.email, m.share_description)
        print ""
        print "B WEEK"
        for m in b_week:
            print "%s => %s" % (m.email, m.share_description)
        print ""






