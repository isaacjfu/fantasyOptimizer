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
access_token = '1pC8b8.Ypgtjpv3uxLAr4iyrwMP7jHxgN5TmBBgiFUqzREGycwbrWQ1TfHQJSn3BFG.CCJqwPEOVQePG28sUZrYxz8yqGvZvvojW8AuTCR7DC7SD1vfedBOT8_3PB4xdsSudq5LY.P467Z1yrGOEvlzGkJlPocqBxTydOrU_noF2Wy366YPY7yPqMiqsI2L.cCD7XeDKR8KfImI4tK0AXc6rustwRniw6jIwnBbZAEnDIbJ6x5PfMYS0FFE33T7HdfBF6a_coUS.la1nU8YVlyr1GPOhc0LkgpwIlen8HDSBnIii9Rzw6Tqlz9kYoOV_LGczFPNoeRR._m5RAq5ZIg4OUBqhCsRXjLN.NZOSHTSsl1XMcNrLR5h6YWeMv7KogKZ8A11waOVbDzmQFzjr1hUp7spWdYH2BCM9W8wwW_qAoFnd.bTf1u0HF.z6Xkvatnih_qHjjd6.Onc3H.TdjOXWkCTuISeYurJzo2WWGo6ts5MFLB9hRDbv99aAOvNf8KagxqEGse4heNJRMSZ7SwSKNSycnKPEIYKBSwy1ZIMzsesikGVeZWfK7bDPYZI_JvuRWeGF.M4IjYKPLR9qCNFudyQeeeBYS_GxFS8XxKDI1d6agKtErXxifAVVuhTjA49LGVptXj0cQ9mqX8_85SRabaM1fU2xhLbPL9r8s28_NkFf0.06t2yHPQyvgc5D9yoZ9JTLW8IryZBseXETEgWpUFA6Bkk7ObHOPxiusuQNPNyvZ1287OdxxHdv0wSLH7KCdGfngghsd584_BcVHyRfDV1zRlFA7LZhbHxdeHGuBgnJKfnE4D671w.jwoj9z4Pg7Hd3BpCip9unwtpIxv1N.CfgWbZn7nkPCRXzjIkHB2y8uTc.eUJH9g3hSz28L2kqEcdp0KBx3k7fvVNVA2TKEK6GiEj1'

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
    start_idx = 0
    end = False
    players = {}

    while(not end):
        u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/players;sort=NAME;start={start_idx}'
        r = requests.get(u,headers = h)
        encoded = r.text.encode(encoding = 'ascii', errors = 'ignore').decode("utf-8")
        root = strip_namespace(encoded)
        league_node = root.find('league')
        players_node =  league_node.find('players')
        
        count = players_node.attrib
        count = (int) (count['count'])
        if count < 25:
            end = True
        start_idx += count

        for player in players_node.findall('player'):
            name_node = player.find('name')
            full_name = name_node.find('full').text
            players[player.find('player_id').text] = full_name
            pass

    f = open("test.txt", "w")
    f.write(r.text)
    f.close()

    print(players)
    print(len(players))

        
    

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