from flask import Flask, request
from dotenv import load_dotenv
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo, cumestatsteamgames, playernextngames
from nba_api.stats.static import players
import os
import requests
import json
import webbrowser
import xml.etree.ElementTree as ET


load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
league_id = os.getenv('LEAGUE_ID')
redirect_uri = 'https://redirectmeto.com/http://localhost:5000/redirect'
url_base = 'localhost:5000'
access_token =  'Rbe387qYpgsLbWTT_MjFdPtFYB8buY4EDQvQ68f15GBaxk6g.RVbQ.P6mdT60LUvIK2xBIKARv1rQ4Z.x8IhEUSAvoNJpnFHe5uJolaGvHt_5vDMuk4MWTZcUdIemFb_DwbenkwRn7izkTuLaS.480Qdj8h8o7DNlL6ifbRCbFWGBhWhF6A2sspn3ZATusyGEiP5p9t4MHMMCb74mkCq8MB0Nlg5DKzJ6f6ZHpfsXBUetHDMhnwnijr9neadoA7o1VJPJan5A3hTCY0hyu1UuMxG7OzBoPYC8pnrPScaJ6cDYR88Kv83wuq_tTEv9VtVW4eGK1eZlqeHESlnxDS6eZgb_yr5dweLatGnkn7ynLlT8Tj59akdzetuiXg_2LZTyFP.nWl6ZwbUtgesvsBHs9B07vzV7DHneSqzOuBofZVVpVUCeA5An8NfUCHnfZIIMBGmuVSglOcTs4fAqDtji7xcVkVfiNJcR6QNUtETFLhU3O_.O56dmpofvF22RUMhoRtHlaH7GH7ns1pPl3XSzouKX0sdPoWmXpv_g6BaGuEYUuuI507Rhbt8ULS91_VNY1194yKiTYRUyDyOyQ0iak5_N3EUXWO1QnuMXnFI4F4fa3.2AkyugBl1uJJP82cF0HutF2IkcL2_ea34gLeG2PvrFTfC3_593FCXYw2vqi.sy4p5D9lA.TMNF1QYAzQyQ61iP7ibcmWQ5ILAPMvoAkzKFWNzY84fu46MEi8S3KmfHhcYnOpAzbq4AOmyG5HONHqkgByZL08vreKDXPMiCdx86jFkPzRCun2DQFMcxsBw09IL5iy.Z3CEdHtL0X5p309LbwapcvXaR6f.x5wz27CCJm73_o28Wtsj8nWj8Ku5AWkRHAa2EzLVrzorJJYg2RdaBGwcBgHYC4adlOQTxKY_ec.v7WLB'

CONST_CURRENT_SEASON = '2023-24'
# may need to refactor into the settings query
CONST_STAT_IDENTIFER = {
    '9004003' : 'FGM/A',
    '9007006' : 'FTM/A',
    '10' : '3PM',
    '12' : 'PTS',
    '15' : 'REB',
    '16' : 'AST',
    '17' : 'STL',
    '18' : 'BLK',
    '19' : 'TOV'
}

all_players = players.get_active_players()

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
    #players = players_query(h,l_id)
    #team = team_query(h,l_id) 
    matchup = matchup_query(h,l_id)

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
    f = open("settings.txt", "w")
    f.write(r.text)
    f.close()
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
            team_name = t_elem.find('editorial_team_abbr').text
            jersey_number = t_elem.find('uniform_number').text

            player_key = f"{full_name}/{team_name}/{jersey_number}"
            teams[key]['roster'].append(player_key)
    print(teams)

    return teams

def players_query(h,l_id):
    players = {}
    players_query_helper(h,l_id,players,'T')
    players_query_helper(h,l_id,players,'FA')
    print(players) 

def players_query_helper(h,l_id,playersDictionary,status):
    f = open('playerStats.json')
    player_stats = json.load(f)
    start_idx = 0
    end = False
    while(not end):
        u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/players;status={status};start={start_idx}/stats'
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
            player_id = player.find('player_id').text
            team_name = player.find('editorial_team_abbr').text
            jersey_number = player.find('uniform_number').text

            player_key = f"{full_name}/{team_name}/{jersey_number}"
            #general information
            playersDictionary[player_key] = {}
            playersDictionary[player_key]['name'] = full_name
            playersDictionary[player_key]['rostered'] = status

            #inj status
            injury_node = player.find('status')
            if injury_node == None:
                playersDictionary[player_key]['injured'] = '0'
            else:
                playersDictionary[player_key]['injured'] = '1'
            
            # positions
            eligible_node = player.find('eligible_positions')
            playersDictionary[player_key]['pos'] = []
            for pos in eligible_node.findall('position'):
                playersDictionary[player_key]['pos'].append(pos.text)
            
            # stats
            # potentially need to filter only out the stats that i need. when im adding compatibility with different league settings
            playersDictionary[player_key]['stats'] = player_stats[player_key]['stats'] if player_stats.get(player_key) != None else []

            #schedule
            playersDictionary[player_key]['schedule'] = player_stats[player_key]['schedule'] if player_stats.get(player_key) != None else []
    
def matchup_query(h,l_id):
    matchups_dict = {
        'start' : '',
        'end' : '',
        'matchups': []
    }

    u = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{l_id}/scoreboard'
    r = requests.get(u,headers = h)
    encoded = r.text.encode(encoding = 'ascii', errors = 'ignore').decode("utf-8")
    root = strip_namespace(encoded)
    
    for matchups in root.iter('matchups'):
        for matchup in matchups.findall('matchup'):
            matchups_dict['start'] = matchup.find('week_start').text
            matchups_dict['end'] = matchup.find('week_end').text
            teams_node = matchup.find('teams')
            matchup = {
                'team_1' : '',
                'team_2': '',
                'team_1_stats' : [],
                'team_2_stats' : []
            }
            count = 1
            for team in teams_node.findall('team'):
                team_str = f'team_{count}'
                team_stats_str = f'team_{count}_stats'
                matchup[team_str] = team.find('team_key').text
                team_stats = team.find('team_stats')
                stats_node = team_stats.find('stats')
                for stat in stats_node.findall('stat'):
                    stat_id = stat.find('stat_id').text
                    if CONST_STAT_IDENTIFER.get(stat_id) != None:
                        matchup[team_stats_str].append(stat.find('value').text)
                count += 1
                
            matchups_dict['matchups'].append(matchup)
    print(matchups_dict)
    return matchups_dict
    # f = open("test.txt","w")
    # f.write(encoded)
    # f.close()

def import_player_data():
    #print(all_players)
    #for i in range(0,len(all_players)):
    player_dict = {}
    f = open('teamSchedules.json')
    teamSchedules = json.load(f)
    for i in range(0,len(all_players)):
        player = all_players[i]
        career_stats = playercareerstats.PlayerCareerStats(per_mode36 = "PerGame", player_id = player['id']).get_json()
        player_info = commonplayerinfo.CommonPlayerInfo(player_id = player['id']).get_json()
        career_obj = json.loads(career_stats)
        player_obj = json.loads(player_info)
        index = 0
        for i in range(len(career_obj["resultSets"])):
            if career_obj["resultSets"][i]["name"] == "SeasonTotalsRegularSeason":
                index = i
                break
        player_info = player_obj['resultSets'][0]['rowSet'][0]
        player_key = f'{player_info[3]}/{player_info[20]}/{player_info[14]}'
        if len(career_obj['resultSets'][index]['rowSet']) != 0:
            season_stats = career_obj["resultSets"][index]["rowSet"][-1]
            if season_stats[1] == CONST_CURRENT_SEASON:
                filtered_stats = {
                    "season": season_stats[1],
                    "gp": season_stats[6],
                    "fgm": season_stats[9],
                    "fga": season_stats[10],
                    'ftm': season_stats[15],
                    'fta': season_stats[16],
                    "pts": season_stats[26],
                    "reb": season_stats[20],
                    "ast": season_stats[21],
                    "3pm": season_stats[12],
                    "stl" : season_stats[22],
                    "blk" : season_stats[23],
                    "tov" : season_stats[24]
                }
            else:
                filtered_stats = {
                    "season": CONST_CURRENT_SEASON,
                    "gp": '0',
                    "fgm": '0',
                    "fga": '0',
                    'ftm': '0',
                    'fta': '0',
                    "pts": '0',
                    "reb": '0',
                    "ast": '0',
                    "3pm": '0',
                    "stl" : '0',
                    "blk" : '0',
                    "tov" : '0'
                }
            player_dict[player_key] = {
                'stats' : filtered_stats,
                'schedule' : teamSchedules[player_obj['resultSets'][0]['rowSet'][0][20]] if player_obj['resultSets'][0]['rowSet'][0][20] != '' else {}
            }
        print(player_key)
    print(len(player_dict))

    with open('playerStats.json', "w") as outfile:
        json.dump(player_dict,outfile,indent = 2)

def import_team_data():
    team_schedules = {

    }
    r = requests.get("https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json").json()
    games = r['leagueSchedule']['gameDates']

    for date in games:
        print(date['gameDate'])
        for game in date['games']:
            print(game['gameLabel'])
            if (game['gameLabel'] == ''):
                if team_schedules.get(game['homeTeam']['teamTricode']) == None:
                    team_schedules[game['homeTeam']['teamTricode']] = [date['gameDate']]
                else:
                    team_schedules[game['homeTeam']['teamTricode']].append(date['gameDate'])
                if team_schedules.get(game['awayTeam']['teamTricode']) == None:
                    team_schedules[game['awayTeam']['teamTricode']] = [date['gameDate']]
                else:
                    team_schedules[game['awayTeam']['teamTricode']].append(date['gameDate'])
    with open('teamSchedules.json', "w") as outfile:
        json.dump(team_schedules,outfile,indent = 2)

def test_function():
    pass

#test_function()
#import_team_data() 
#import_player_data()
