from flask import Flask, request
from dotenv import load_dotenv
import os
import requests
import webbrowser
import xml.etree.ElementTree as ET

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
league_id = os.getenv('LEAGUE_ID')
redirect_uri = 'https://redirectmeto.com/http://localhost:5000/redirect'
url_base = 'localhost:5000'
access_token = 'BHfMUMWYpgvrjbR5Ou8w91tgvZxJBRIiDUBNL.VD4feGXQg0jBy7sHsw3ejXqGbYKT4SB6gViRJZ5aI0yuE5Q42PCM_ZHm_g47dl6Jo10zVZ._rh786WWGDETq6BjBNcN4pMOVHt.J_c5gtL.vvS0CThXopm2eYBAfGe3QNUJYENOjbNXF3epk1RYgYvQvnDeONEbhBQICFBczc4vp0IoSJcALRRMsQj5hGMijonmdEKGTY7iwAwqrC.R5PIc3qBIq0vxqJxyT8A8wD7zEExKa8ktW62A38Nz5xIveU914ffQqWG_ydZaZ7B.WEF8752HkCUOTgIOFoJzAtgw9K5C.Cxd6oMZ74vEFOO5cHTmPXLXS._KkCtKiKCAClfzPS7dcfytGtclKuHFSR4KkxRoBrVmCaYHaCGzVwXC88VbdBuXEbpdfET9dmff2fH5yAgbY3C8cYQK8AdJbv5KsX.OYIfyJgsO2ulobT4DpInK3mWg21tC4AmREHo3vyksbMeFG_2xjtsAeQB.ebxsPbLuB2SMxAMOMD5aMmSrsqaVMk3rT8029Px1805jPS_jo8I6WiOpNxmVs5hC2kFEi6hKWZZM42.JOp35BkKctc4sjIhbHPxqWobklG0IfLjWItMYfFjEWn.GiLb1TG2tjP6JaZDM_qcccE6A6tmWlpEQpCd39tojYop_WcU2VYYMBN9_bHSqWMJQUUSjFtwFoh_h1dv7LEsqyj1UGdus1gansjjZhOE6q7hPmF7SckSvyMrXdpdDTuQ93LzOWQYTB6qFomV_CBR0r4Lsq5Wl2F1Cc62Z5RFssKLK0b22r8DZplGg6PhSlaxrP4KxqmmmHw9fs6I5d_u4LiP9F65uURkvhxFPsfQIws3F8Zz0rRbobr8pSQPxPu59vCm55d7NwsuSeoX7IMqUV1L'

def request_handler():
    
    u = f'https://api.login.yahoo.com/oauth2/request_auth?'
    p = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type' : 'code'
    }
    print(u)
    r = requests.get(u,p)
    webbrowser.open(r.url)

app = Flask(__name__)
@app.route("/")
def hello_world():
    request_handler()
    return "hi"

@app.route("/redirect", methods = ['GET', 'POST'])
def redirect():
    code = request.args.get('code')
    u = f"https://api.login.yahoo.com/oauth2/get_token?"
    p = {
        'client_id' : client_id,
        'client_secret' : client_secret,
        'redirect_uri': redirect_uri,
        'code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.post(u,p)
    response = r.json()
    print(response)
    token = response['access_token']
    print(token)
    return token

@app.route('/controller', methods = ['GET','POST'])
def controller():
    #token = request.args.get('token')
    l_id = f'nba.l.{league_id}'
    r_string = query(access_token,l_id)
    return r_string

def query(token, l_id):
    h = {
        'Authorization': f'Bearer {token}'
    }

    #settings = settings_query(h,l_id)
    players = players_query(h,l_id)
    #team = team_query(h,l_id) 
    #matchup = matchup_query(h,l_id)

    return "asdf"

def strip_namespace(xml_string):
    root = ET.fromstring(xml_string)
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}',1)[1]
    return root

def settings_query(h,l_id):
    d = {
        'roster_spots': [],
        'categories': [],
        'max_weekly_adds': 0,
        'waiver_time': 0,
        'current_week' : 0
    }
    u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/settings'
    r = requests.get(u,headers = h)
    root = strip_namespace(r.text)
    
    for elem in root.iter('roster_position'):
        pos = elem.find('position').text
        amt = int(elem.find('count').text)
        for i in range(amt):
            d['roster_spots'].append(pos)
    for elem in root.iter('stats'):
        for stat in elem.findall('stat'):
            name = stat.find('display_name').text
            d['categories'].append(name)
    for elem in root.iter('waiver_time'):
        d['waiver_time'] = elem.text
    for elem in root.iter('max_weekly_adds'):
        d['max_weekly_adds'] = elem.text
    for elem in root.iter('current_week'):
        d['current_week'] = elem.text

    return d

def team_query(h,l_id):
    u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/standings'
    r = requests.get(u,headers = h)
    encoded = r.text.encode(encoding = 'ascii', errors = 'ignore').decode("utf-8")
    root = strip_namespace(encoded)
    teams = {}
    for elem in root.iter('team'):
        key = elem.find('team_key').text
        name = elem.find('name').text
        team_url = f'https://fantasysports.yahooapis.com/fantasy/v2/team/{key}/roster/players'
        t_r = requests.get(team_url,headers = h)
        t_encoded = t_r.text.encode(encoding = 'ascii', errors = 'ignore').decode("utf-8")
        t_root = strip_namespace(t_encoded)
        teams[key] = {
            'name' : name,
            'roster' : []
        }
        for t_elem in t_root.iter('player'):
            name_pos = t_elem.find('name')
            full_name = name_pos.find('full').text
            print(full_name)
            teams[key]['roster'].append(full_name)
    print(teams)

    return teams

def players_query(h,l_id):
    u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/players;search=a'
    r = requests.get(u,headers = h)
    print(r.text)
    encoded = r.text.encode(encoding = 'ascii', errors = 'ignore').decode("utf-8")
    root = strip_namespace(encoded)
    f = open("test.txt", "w")
    f.write(r.text)
    f.close()

def matchup_query(h,l_id):
    team_1 = {
        'cat_totals': [],
        'roster': []
    }
    team_2 = {
        'cat_totals': [],
        'roster' : []
    }
    u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/scoreboard'
    r = requests.get(u,headers = h)
    encoded = r.text.encode(encoding = 'ascii', errors = 'ignore').decode("utf-8")

    f = open("test.txt","w")
    f.write(encoded)
    f.close()
    root = strip_namespace(encoded)
    
    print(ET.tostring(root).decode())
    for elem in root.iter('matchup'):
        print(elem)

    print("hello")

def test_function():
    team_1 = {
        'cat_totals': [],
        'roster': []
    }
    team_2 = {
        'cat_totals': [],
        'roster' : []
    }
    with open('test.txt', 'r') as file:
        data = file.read()
    root = strip_namespace(data)
    
    print(ET.tostring(root).decode())
    for elem in root.iter('matchup'):
        print(elem)




#test_function()