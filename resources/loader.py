import pkg_resources

def load_geoip():
    import geoip2.database

    
    resource_package = __name__
    filename = pkg_resources.resource_filename(resource_package, 'GeoIP2-City.mmdb') #Download and place GeoIP2-City.mmdb in resource folder
    return geoip2.database.Reader(filename)


if __name__ == '__main__':
    import geoip2.database

    gp= geoip2.database.Reader('GeoIP2-City.mmdb')
    print(gp.city('128.101.101.101').city.name)

    # resource_package = __name__
    # filename = pkg_resources.resource_filename(resource_package, 'GeoIP2-City.mmdb')
    # print(filename)