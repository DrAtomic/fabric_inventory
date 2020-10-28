import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import numpy as np
import webcolors
from PIL import Image
from io import BytesIO
import sys
# access google sheets ########################################################
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client = gspread.authorize(creds)

sheet = client.open("inventory").sheet1

data = sheet.get_all_records()

# manipulate image ############################################################
#fabricdb = [color,type_of_facbric,cost_per_yard,yards,picture]


path_to_image = sys.argv[1]
type_of_fabric = sys.argv[2]
cost_of_fabric = sys.argv[3]
length_of_fabric = sys.argv[4]

cost_per_yard = float(cost_of_fabric) / float(length_of_fabric)

# color classifier
def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

# get image and avg

im = Image.open(path_to_image)
image = np.asarray(im)
width, height,d = image.shape
center_x = width/2
center_y = height/2

left =round(center_x-150)
top =round(center_y+150)
right =round(center_x+150)
bottom =round(center_y-150)
croped = image[left:right,bottom:top]
im1 = Image.fromarray(croped)

buffer = BytesIO()
im1.save(buffer, format="JPEG")
myimage = buffer.getvalue()
bytes_data = base64.b64encode(myimage)

average = (croped.sum(axis=1).sum(axis=0)) / (croped.shape[0]*croped.shape[1])


color_name = closest_color(average)
# end of color classifier

#begin append
row = [color_name, type_of_fabric, cost_per_yard, length_of_fabric, str(bytes_data)]
sheet.append_row(row)

