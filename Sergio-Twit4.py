from TwitterSearch import *
import arcpy
from geopy import geocoders
from arcpy import env
arcpy.env.overwriteOutput = True


filelocation = "C:\Users\sergiohernandez\UWMSGT"  #WHERE YOU WANT YOUR NEW FILE
#fc = "TwitterData.shp"      ##place to put turtle feature class
spatialref = arcpy.SpatialReference ('WGS 1984')
#arcpy.management.CreateFeatureclass(filelocation, fc, "POINT", "", "", "", spatialref)
env.workspace = "C:\Users\sergiohernandez\UWMSGT" #location of file creation

var1 = 3857 # WKID numeric code for spatial referenceing. Sam's voodoo
spat = arcpy.SpatialReference(var1) # Setting spatial ref. More of Sam's voodoo
fc = "TwitterData.shp" # feature class file name

arcpy.management.CreateFeatureclass(filelocation, fc, "POINT", "", "", "", spatialref)


# Feature class name, Field name, field type, blah, blah, length, blah, allows nulls.
arcpy.AddField_management(fc, "NAME", "TEXT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "TWEETED", "TEXT", "", "", 100, "", "NULLABLE")
arcpy.AddField_management(fc, "SCRN_NAM", "TEXT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "LAT", "FLOAT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "LONG", "FLOAT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "DATE", "TEXT", "", "", 30, "", "NULLABLE")

def geo(location):
    g = geocoders.GoogleV3()
    loc = g.geocode(location)
    return loc.latitude, loc.longitude

try:
    tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
    tso.set_keywords(['Flu'])  # let's define all words we would like to have a look for
#tso.add_keyword(['flu'])
    #tso.add_keyword(['cough'])
    #tso.add_keyword(['fever'])
    #tso.add_keyword(['Cold'])
    #tso.add_keyword(['Fever'])
    #tso.add_keyword(['ill'])
    #tso.add_keyword(['Ill'])
    #tso.add_keyword(['feel sick'])
    #tso.add_keyword(['Feel sick'])
    #tso.add_keyword(['Cough'])
    tso.set_geocode(47.2414, -122.4594, 50, False) #Sets location and range true for meters false for miles
    tso.set_include_entities(False)  # and don't give us all those entity information

# Object creation with secret token
    ts = TwitterSearch(
        consumer_key = 'FFlNeVBDgo8Mw5ZfrYVpkiluV',
        consumer_secret = 'LIb9nNTxAQtzrmRmfB6UvnroUhxEbgV13NBE2wkgKQcGQYbhFb',
        access_token = '2865011609-0HWPDUJntfj5dgVX2FacK6q6rqlYYz5mI4cVFW9',
        access_token_secret = 'BCYcDKuDnwcZq7cLCPZwIAoOqxJuVLXNSCnpQH7u9o7xM'
     ) 


    curs1 = arcpy.da.InsertCursor("C:\Users\sergiohernandez\UWMSGT\TwitterData.shp", "SHAPE@XY")

    # For every tweet indexed using "search_tweets_iterable(tso) do some stuff.
    for tweet in ts.search_tweets_iterable(tso):

        # But only do some stuff if the tweet has "place" info aka geo-tagged (sort of).
        if tweet['place'] is not None:

            # Create update cursor for populating fields. I have created a list of field names I want updated.
            curs2 = arcpy.da.UpdateCursor("C:\Users\sergiohernandez\UWMSGT\TwitterData.shp",
                                          ["NAME", "TWEETED", "SCRN_NAM", "LAT", "LONG", "DATE"])

            # This begins an ugly bit of variable creation
            # G grabs coordinate info from tweets and put them in a Dictionary,
            #but it isn't very usable, for me. lots of extra stuff I'm not good at working with.
            G = (tweet['coordinates'])

            # So this bit turns the dict. G into a list of items. {Key:Value , Key:Value} becomes [key,value,key,value]
            # Specifically {(some_junk: some_other_junk),(more_junk : [long,lat])...
            H = list(reduce(lambda x, y: x + y, G.items())) # What the hell is Lambda?
            # became [some_junk, some_other_junk, more_junk, [long,lat]]


            # L,V,U, break down the list objects and eventually pulls the lat, long in a way so that it's usable to me.
            # L specifically pulls the 4th item in the list H which happens to be long, lat.
            L = H[3]
            # L becomes just [long,lat]

            # V creates a list to put some stuff.
            V = []

            # U grabs the second value from L which is Lat, and the first value long.
            U = L[1], L[0]
            # U [lat,long]

            # But I couldn't get U to work the way it was so I appended it to V.
            # now that lat, long are in the right order lets append that to V to be used by the insert cursor.
            V.append(U)

            # Inserts the lat,long as a point object, or as rows in your shapefile.
            curs1.insertRow(V)

            # More ugly variables.
            # B is the Tweeters user name. Tweet is a function of twitter_search_order
            # 'user' is a class of tweet, and 'name' is class of 'user'
            B = (tweet['user']['name'])

            # A returns the text of the tweet. I'd like to clean this up
            # and parse through for specific text, but yeah someother time.
            A = (tweet['text'])

            # D returns screen name much the same way that B returned user name.
            D = (tweet['user']['screen_name'])

            # Sets X as lat value, just like above, but this time for using it as a field value.
            X = L[1]

            # Same thing for Y.
            Y = L[0]

            # F returns a time date stamp.
            F = (tweet['created_at'])


            # heres where I had the most trouble. Its "simple" now that I figured this out.
            # but I spent hours trying to get this to work right.

            # for every row that the update cursor goes through. Do some stuff...
            for row in curs2:
                # essentially;

                # Note that 'TWEETER' is in the [0] position of the update cursor field list
                # example ---> ["TWEETER", "TWEETED", "SCRN_NAM", "LAT", "LONG", "DATE"]
                #                ^row[0]^   ^row[1]^   ^row[2]^    etc.

                # if a row has a 'TWEETER' field that is " " empty...
                if row[0] == " ":
                    # fill it with the information in variable B...
                    row[0] = B
                    # Now update that row/field.
                    curs2.updateRow(row)
                elif row[1] == " ":
                    row[1] = A
                    curs2.updateRow(row)
                elif row[2] == " ":
                    row[2] = D
                    curs2.updateRow(row)
                elif row[3] == 0:
                    row[3] = X
                    curs2.updateRow(row)
                elif row[4] == 0:
                    row[4] = Y
                    curs2.updateRow(row)
                elif row[5] == " ":
                    row[5] = F
                    curs2.updateRow(row)

            print X
            print Y

except:
    print "blah"
