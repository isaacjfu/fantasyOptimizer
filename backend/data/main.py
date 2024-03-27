import requests
import json
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo, cumestatsteamgames, playernextngames
from nba_api.stats.static import players

CONST_CURRENT_SEASON = '2023-24'
all_players = players.get_active_players()

def import_player_data():
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

import_team_data()
import_player_data() 