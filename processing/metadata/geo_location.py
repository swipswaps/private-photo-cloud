def LocationByGPS(gps_latitude=None, gps_longitude=None):
    import geocoder

    if not gps_latitude or not gps_longitude:
        return

    print(geocoder.osm([gps_latitude, gps_longitude], method='reverse'))
