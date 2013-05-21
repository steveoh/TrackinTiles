import gspread, os, pickle, ConfigParser, requests, smtplib
from jinja2 import Template
from datetime import datetime, timedelta
from email.mime.text import MIMEText

def get_credentials():
    print 'getting credentials'
    
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
    print 'converting to milliseconds'
    
    offset = stop - start
    milli = (offset.days * 24 * 60 * 60 + offset.seconds) * 1000 + offset.microseconds / 1000.0
    
    if milli > 5000:
        notify(milli)
        
    return milli

def notify(time):
    print 'notifying you'
    to = 'sgourley@utah.gov'
    sender = 'no-reply@utah.gov'
    
    msg = MIMEText('The basemaps are taking {} milliseconds to load a tile'.format(time))
    msg['Subject'] = 'Basemaps are slowing down'
    msg['From'] = sender
    msg['To'] = to
    
    s = smtplib.SMTP('send.state.ut.us:25')
    s.sendmail(sender, [to], msg.as_string())
    s.quit()

def request_tile():
    starttime = datetime.now()
    r = requests.get('http://mapserv.utah.gov/arcgis/rest/services/BaseMaps/Vector/MapServer/tile/4/69/68')
    endtime = datetime.now()
    
    return milliseconds(starttime, endtime)

sheet = get_spreadsheet('CacheTileTimes')
sheet.append_row([datetime.now(), request_tile()])
print 'done'

