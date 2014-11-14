import arcpy, turtle, fileinput, string

#arcpy.env.overwriteOutput = True #be able to overwrite data
filelocation = "C:/Users/sergioh/Downloads/501lab6"  #WHERE YOU WANT YOUR NEW FILE
fc = "turtle_poly.shp"      ##place to put turtle feature class
spatialref = arcpy.SpatialReference ('WGS 1984')
arcpy.management.CreateFeatureclass(filelocation, fc, "POLYGON", "", "", "", spatialref)

#arcpy.management.AddField(fc, "X", "FLOAT")
#arcpy.management.AddField(fc, "Y", "FLOAT")


window = turtle.Screen()
window.bgcolor("lightpink")
steve= turtle.Turtle()
steve.color("green")
str_sides = input("How many sides do you want on your shape?") # takes input 
sides = int(str_sides)                                         # changes input string to integer
print(sides)
point = arcpy.Point()
array = arcpy.Array() # need this defined before the loop so that it can access it
for i in range (sides):	
    steve.forward(50)
    print steve.position()
    steve.right(360/sides)
    point.X, point.Y = steve.position()
    array.add(point) # adds points to the array



polygon = arcpy.Polygon(array)
cursIns = arcpy.da.InsertCursor(fc, ["SHAPE@"])
cursIns.insertRow([polygon])

del cursIns
