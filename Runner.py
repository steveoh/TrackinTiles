import gspread, os, pickle, ConfigParser, requests, smtplib, time
from jinja2 import Template
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from random import choice

def load_secrets():
    print 'getting credentials'
    
    config = ConfigParser.RawConfigParser()
    
    secrets = 'secrets.cfg'
    
    config.read(secrets)
    
    user = config.get("Google", "username")
    password = config.get("Google", "password")
    notify = config.get("Notify", "email")
    mail_server = config.get("Email", "server")
    url = config.get("Track", "url")
    
    return user, password, notify, mail_server, url 

def get_spreadsheet(spreadsheet):
    print 'getting data from {}'.format(spreadsheet) 
    
    gc = None
    
    try:
        gc = pickle.load(open('conf.p', 'rb'))
    except: 
        pass
    
    if gc is None:    
        gc = gspread.login(secrets[0], secrets[1])
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
    to = secrets[2]
    sender = 'no-reply@utah.gov'
    
    msg = MIMEText('The basemaps are taking {} milliseconds to load a tile'.format(time))
    msg['Subject'] = 'Basemaps are slowing down'
    msg['From'] = sender
    msg['To'] = to
    
    s = smtplib.SMTP(secrets[3])
    s.sendmail(sender, [to], msg.as_string())
    s.quit()

def request_tile():
    basemaps = ['Vector', 'Terrain', 'Hybrid', 'Imagery', 'Topo', 'Lite', 'Hillshade']
    map_name = choice(basemaps)
    
    print 'requesting tile for {}'.format(map_name)
    
    starttime = datetime.now()
    r = requests.get(secrets[4].format(map_name))
    endtime = datetime.now()
    
    return milliseconds(starttime, endtime)

secrets = load_secrets()
sheet = get_spreadsheet('CacheTileTimes')

while True:
    sheet.append_row([datetime.now(), request_tile()])
    print 'sleeping 30 seconds'
    time.sleep(30)

