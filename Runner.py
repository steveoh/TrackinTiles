import gspread, os, pickle, ConfigParser, requests
from jinja2 import Template
from datetime import datetime, timedelta

def get_credentials():
    config = ConfigParser.RawConfigParser()
    
    secrets = 'secrets.cfg'
    
    config.read(secrets)
    
    user = config.get("Google", "username")
    password = config.get("Google", "password")
    
    return user, password

def get_spreadsheet(spreadsheet):
    print 'getting data from {}'.format(spreadsheet) 
    
    gc = None
    
    try:
        gc = pickle.load(open('conf.p', 'rb'))
    except: 
        pass
    
    if gc is None:    
        creds = get_credentials() 
        gc = gspread.login(creds[0], creds[1])
        pickle.dump(gc,open('conf.p','wb'))
    
    # Open a worksheet from spreadsheet with one shot
    return gc.open(spreadsheet).sheet1

def milliseconds(start, stop):
    offset = stop - start
    return (offset.days * 24 * 60 * 60 + offset.seconds) * 1000 + offset.microseconds / 1000.0

def request_tile():
    starttime = datetime.now()
    r = requests.get('http://mapserv.utah.gov/arcgis/rest/services/BaseMaps/Vector/MapServer/tile/4/69/68')
    endtime = datetime.now()
    
    return milliseconds(starttime, endtime)

sheet = get_spreadsheet('CacheTileTimes')
sheet.append_row([datetime.now(), request_tile()])
print 'done'

