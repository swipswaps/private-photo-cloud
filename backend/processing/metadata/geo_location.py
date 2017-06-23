def LocationByGPS(gps_location=None):
    """
    Options:
    * geopy
        -> from geopy.geocoders import Nominatim
        -> Nominatim().reverse(gps_location, language='ru')
    * API of esosedi -- https://github.com/esosedi/regions/blob/master/geocoder.md
        -> http://data.esosedi.org/geocode/v1?lng=ru&point=50.8982722222222,6.98808611111111
    * http://wiki.openstreetmap.org/wiki/Nominatim#Reverse_Geocoding
        -> http://nominatim.openstreetmap.org/reverse?format=xml&lat=50.8982722222222&lon=6.98808611111111&zoom=18&addressdetails=1&accept-language=ru&extratags=1&namedetails=1
    * geocoder
        -> import geocoder
        -> geocoder.osm(gps_location, method='reverse')
    """
    from geopy.geocoders import Nominatim

    if not gps_location:
        return

    LANGUAGE = 'ru'

    res = Nominatim().reverse((gps_location.x, gps_location.y), language=LANGUAGE)
    return 'location', res.raw['address']
