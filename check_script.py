from GPSPhoto import gpsphoto

def get_data(picture):

    a = gpsphoto.getGPSData(picture)

    try:
        return f"{a['Latitude']},{a['Longitude']}"

    except Exception as e:
        return ("ERROR")



# pic = "image.jpg"
# print(get_data(pic))
