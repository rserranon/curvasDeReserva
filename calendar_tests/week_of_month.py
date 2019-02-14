import datetime
import calendar

# I am assuming that the first week of a month starts with the first monday of a month...
#I *think* my logic is OK - if Monday (0) is the start of the week, then
#any dayof the month minus its own day of week (0,1,2...) must be positive
#if that day is on or after the first monday of the month

def week_of_month(tgtdate):

    days_this_month = calendar.mdays[tgtdate.month]
    for i in range(1, days_this_month):
        d = datetime.date(tgtdate.year, tgtdate.month, i)
        if d.day - d.weekday() > 0:
            startdate = d
            break
    # now we canuse the modulo 7 appraoch
    return (tgtdate - startdate).days //7 + 1

tgtdates = [datetime.date(2018, 1, 1),
            datetime.date(2018, 1, 31)
            ]

for tgtdate in tgtdates:
    print (tgtdate)
    print ("is in week %s" % week_of_month(tgtdate))

print (calendar.month(tgtdate.year,tgtdate.month))

