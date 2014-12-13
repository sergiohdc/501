#Written by Sergio Hernandez
#UWT MSGT program Fall2014
#Special thanks to all who contributed and collaborated.

from TwitterSearch import *
import arcpy
from geopy import geocoders
import time
from arcpy import env
import ftplib
ftp = ftplib.FTP()
arcpy.env.overwriteOutput = True

filelocation = "C:\Users\sergiohernandez\UWMSGT"  #read write location for new files
spatialref = arcpy.SpatialReference ('WGS 1984') # sets non projected spatial reference for output file in ArcGIS
env.workspace = "C:\Users\sergiohernandez\UWMSGT" #location of file creation

var1 = 3857 # WKID numeric code for spatial referenceing. Sam's voodoo
spat = arcpy.SpatialReference(var1) # Setting spatial referece to the above variable
fc = "TwitterData.shp" # feature class file name

arcpy.management.CreateFeatureclass(filelocation, fc, "POINT", "", "", "", spatialref)#Designating the feature class as a point file

# Feature class name, Field name, field type, blah, blah, field character length is in purple, blah, allows nulls.
arcpy.AddField_management(fc, "NAME", "TEXT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "TWEETED", "TEXT", "", "", 100, "", "NULLABLE")
arcpy.AddField_management(fc, "SCRN_NAM", "TEXT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "LAT", "FLOAT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "LNG", "FLOAT", "", "", 20, "", "NULLABLE")
arcpy.AddField_management(fc, "DATE", "TEXT", "", "", 30, "", "NULLABLE")

def geo(location):
    g = geocoders.GoogleV3() #geocoder for returned location data
    loc = g.geocode(location) # setting the variable loc as the above results to be geocoded
    return loc.latitude, loc.longitude # the returned values for loc are split into lat and long
searchlist = ["OutbreakIndicators", "flu", "cold", "cough", "pneumonia", "bronchitis", "fever"] # list of search terms to be used in the following loop

try: # This is the loop that goes through the searchlist for hits
    for hashtag in searchlist:
        tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
        tso.set_keywords([hashtag]) # sets the keyword to the hashtags in the searchlist
    
    tso.set_geocode(47.2414, -122.4594, 50, False) #Sets location and range true for meters false for miles
    tso.set_include_entities(False)  # removes entity information

# Object creation with secret token generated by twitter account
    ts = TwitterSearch(
        consumer_key = 'FFlNeVBDgo8Mw5ZfrYVpkiluV',
        consumer_secret = 'LIb9nNTxAQtzrmRmfB6UvnroUhxEbgV13NBE2wkgKQcGQYbhFb',
        access_token = '2865011609-0HWPDUJntfj5dgVX2FacK6q6rqlYYz5mI4cVFW9',
        access_token_secret = 'BCYcDKuDnwcZq7cLCPZwIAoOqxJuVLXNSCnpQH7u9o7xM'
     ) 

    curs1 = arcpy.da.InsertCursor("C:\Users\sergiohernandez\UWMSGT\TwitterData.shp", ["SHAPE@XY", "LAT", "LNG", "SCRN_NAM", "TWEETED","DATE"]) #shape at xy is a token to be fed lat long

    for tweet in ts.search_tweets_iterable(tso):
            if (tweet['lang'] == 'en'): # sets language to English
                #commented out // lot's of tweets don't have GPS enabled so they wont have coordintes. if you print tweets here you'll see 100% of tweets instead of just tweets with coordinates
                #print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
                if tweet['coordinates'] is not None: #check to see if the tweet is geotagged. If it is not then [0.0, 0.0] or None will be there.

                    print ( '@%s tweeted: %s, on %s' % ( tweet['user']['screen_name'], tweet['text'], tweet['created_at'] ) )
                    C = (tweet['coordinates']) #grab the dictionary containing coordinates
                    C = C.get('coordinates') #get only the coordinates
                    lat = C[1]  #lat is the second binary spot because x,y are mathermatical not geographic x,y = lng, lat
                    lng = C[0]  #sets lng to the first binary position which is mathematical x 
                    print "from geot-tagged location: {}, {}".format(lat, lng) # prints where a geotagged tweet originated from

                elif tweet['place'] is not None: #if tweet place is designated then go through the loop
                    (lat, lng)= geo(tweet['place']['full_name']) 
                    print '(place) Tweeted from (' + str(lat) +', ' +str(lng)+')' #prints the location of the tweet and appends the lat,lang

                elif tweet['user']['location'] is not None: # if the location field is used the go through loop
                    try:
                        (lat, lng) = geo(tweet['user']['location'])
                        print ( '@%s tweeted: %s, on %s' % ( tweet['user']['screen_name'], tweet['text'], tweet['created_at'] ) )
                    except Exception as e:
                        continue
                
                text = str(tweet['text'].encode("utf-8")) # encodes everything as UTF-8 to avoid errors
                username = tweet['user']['screen_name'] # sets the variable username as both user and screen name
                created_at = str(tweet['created_at']) # sets created_at as the string 

                if lat == 0.0:
                    continue
                else:
                    point = arcpy.Point(lng, lat) # sets the point x,y as lat, lng so that arcpy can write it to the shape or point file
                    curs1.insertRow((point, lat, lng, username, text, created_at)) # writes the new data to the new file

            else:
                continue

except (TwitterSearchException) as eg: # error handling
    print "TwitterSearch limit exceded. Please wait 15 minutes"
    time.sleep(1000)
    #update this with timeout error
except Exception as ef:
    print "Error: ", ef
    #continue
    #mxd = arcpy.mapping.MapDocument("current")
    #arcpy.management.MakeFeatureLayer_management(r"C:\Users\sergiohernandez\UWMSGT\TwitterData.shp","Twitter")
    #mxd.save()

   #mxd = arcpy.mapping.MapDocument(r"Y:\Maps\map1.mxd")
#project = "C:/Maps/map1.jpg"
#arcpy.mapping.ExportToJPEG(mxd, project, resolution = 200)
    print "Poop" # the final insult

#import arcpy
#import os

arcpy.MakeFeatureLayer_management(fc, "C:\Users\sergiohernandez\UWMSGT\TwitterData.lyr") # makes a layer from the feature class (input, output file)
arcpy.LayerToKML_conversion("C:\Users\sergiohernandez\UWMSGT\TwitterData.lyr", r"C:\Users\sergiohernandez\UWMSGT\TwitterData.kmz")
# calls the layer to KML tool and creates a .kmz from the layer created above.

ftp.connect('vergil.u.washington.edu', 22)# assigns target ftp host and port (default is port 21)
print ftp.getwelcome()
try:
    print "Logging in..." # attempt to see where the problem lies
    ftp.login("sergioh", "L!ckmynuts01") # login with user, pswd (pardon my language) :)
except:
    "failed to login" # throws exception is credentials are invalid
#ftp.connect(host = 'vergil.u.washington.edu', port = 22)
#ftp.login(user = 'sergioh', passwd = 'L!ckmynuts01')
file = open('C:\Users\sergiohernandez\UWMSGT\TwitterData.kmz','rb')      # file to send not sure what 'rb' is
session.storbinary('STOR TwitterData.kmz', file)     # send the file
file.close()                                    # close file and FTP
session.quit()          # End FTP session

