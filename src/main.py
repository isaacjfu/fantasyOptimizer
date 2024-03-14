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
access_token = 'CJ3nqx2Ypgshg7xs1ITxKUBIeSsZvBiPGZx4tJ3amoSzTjIETPZ4UG7Os63K2jSsLO8DCGm.VjB4fwGr9H_k3nA5tuUp7rI0agBMSob1Sh5oT10.R3Sh89O2SwXcgFGLMFR3Eu0Nb.Iti2Wxyk3aMrbhDAeRPTM4g.Tqmv0m3I6eKebCx4WrbSXfUxbiBhWXYrDeDydYQwZDJsjdrrvioJAvRzSz_JlzIBO5aug6JlWFCdmSALKE2YhQN3PxXkyvr9ywkiumfZfNhkQweAmV4AtVOHAXvfhpAOvIE.xeKxRqfuXbHCViOc5y4xBJdBEU6F49sVPeotAHpDQlkWjhuFfOW1Ziz6bagZ_ST.5D68H463cYY.8QbnFiBdHj8knCbjxYXHID.JXZ1fhegalHwnFWqSh3GDFJr3kfVzeEmPW_t43zMR_T6i__AFyOXNOzzhpBxyLeHgGKXQ_H7lNMfWQbo7mgWNmwZu4GdcuHQv2_PxucOqk8zCrDzhHvQUpMTZzCgTL1dXmSJlpAZRS4WtoU71Vi3qEvZwQY6Ql5WLnCM7fn7PI2h9chwS3MMkKFmuGDfkwE8vQRMJmw8kBpKTjjn_hiQe2k.g2ooqLcsqd9o_97_GgRv782HTQxXNHBKPBF0T_cVe05i0Px_RFIgwzWK9i1il8.3z.9XfK3ca58mG_JpyOKoXcSVtgy_59T1.Unz5wJRiO54RmF97PrxJiEjDbrWUAwtmcXveo9BqjfjzMGYwUcHIf_Gh2_YSoKyIzGWAvdodqLWcGYy6hf.2QvHQ5j1ACaWIVtPYxjzk.VC05fRYZ7OLI3A37wrZ2D3WEbqHmz7wVNDrI71RRTX7hlBOuClUZu6HCGprxfOX2k.cmZO4WUVd_8Vo1N0KxjVrGpWG6Rb7nkLRahjqFBXyqgRCw2sLA-'
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
    cats, spots = settings_query(h,l_id)

    #u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/teams'
    #u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/players;status=A'
    # p = {

    # }
    # r = requests.get(u,headers = h)
    # print (r.status_code)
    # print(r)
    # print(r.headers)
    # print(r.text)
    return cats

def settings_query(h,l_id):
    categories = []
    roster_spots = []
    u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/settings'
    r = requests.get(u,headers = h)
    
    root = ET.fromstring(r.text)
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}',1)[1]
    
    print(ET.tostring(root).decode())
    for elem in root.iter('roster_position'):
        print(elem)
        pos = elem.find('position').text
        amt = int(elem.find('count').text)
        for i in range(amt):
            roster_spots.append(pos)
    for elem in root.iter('stats'):
        for stat in elem.findall('stat'):
            name = stat.find('display_name').text
            categories.append(name)

    print(categories)
    print(roster_spots)

    f = open("test.txt","w")
    f.write(r.text)
    f.close()
    return categories, roster_spots

def test_function():
    roster_spots = []
    categories = []
    with open('test.txt', 'r') as file:
        data = file.read()
    root = ET.fromstring(data)
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}',1)[1]
    
    print(ET.tostring(root).decode())
    for elem in root.iter('roster_position'):
        print(elem)
        pos = elem.find('position').text
        amt = int(elem.find('count').text)
        for i in range(amt):
            roster_spots.append(pos)
    for elem in root.iter('stats'):
        for stat in elem.findall('stat'):
            name = stat.find('display_name').text
            categories.append(name)
    print(categories)
    print(roster_spots)




test_function()