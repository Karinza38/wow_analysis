__author__ = 'hsdk.bd'

# import urllib2
# import json
#
# response = urllib2.urlopen('https://us.api.battle.net/wow/character/Rexxar/Gonkion?locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848')
# data = json.load(response)

import requests
import csv
import ast
import numpy as np

#battleType: 2v2, etc.
def getTop100pvpers( battleType ):
    r = requests.get("https://us.api.battle.net/wow/leaderboard/"+battleType+"2v2?locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
    result = r.json()

    players = []
    playerAndRealmNames = []

    # get top 100 PVP player names
    for row in result["rows"]:
        if len(players) >= 100:
            break;
        players += [row]
        #playerNames += row["name"]
        playerAndRealmNames.append( [ row["name"], row["realmName"] ] )

    return playerAndRealmNames

def getAndSavePlayerGuildNames():
    guildNamesAndRealm = []
    playerAndRealmNames = getTop100pvpers("2v2")
    # for each player, get their guild
    for nameRealmPair in playerAndRealmNames:
        r = requests.get("https://us.api.battle.net/wow/character/"+nameRealmPair[1]+"/"+nameRealmPair[0]+"?fields=guild&locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
        result = r.json()
        if "guild" in result:
            guildNamesAndRealm.append( [ nameRealmPair[0], nameRealmPair[1], result["guild"]["name"] ] )
        else:
            #noGuildPlayerNames.append( nameRealmPair )
            guildNamesAndRealm.append( [ nameRealmPair[0], nameRealmPair[1], "" ] )

    #write to csv file
    with open(filename2v2, "w", newline="", encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['player_name', 'realm_name', 'guild_name'])
        for item in guildNamesAndRealm:
            writer.writerow(item)

def getAndSaveFilteredGuilds( guildNamesAndRealm ):
    for player_realm_guild in guildNamesAndRealm:
        r = requests.get("https://us.api.battle.net/wow/guild/"+player_realm_guild[1]+"/"+player_realm_guild[2]+"?fields=achievements&locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
        result = r.json()
        if "achievements" in result:
            achievementIds = result["achievements"]["achievementsCompleted"]
            filtered_ids = [i for i in achievementIds if i in achievementsToFind]
            if len(filtered_ids) > 0:
                guildsWithWantedAchievements.append( [ player_realm_guild[2], player_realm_guild[1], filtered_ids ] )

    #write to csv file
    with open(filename2v2guildsFiltered, "w", newline="", encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['guild_name', 'realm_name', 'achievements'])
        for item in guildsWithWantedAchievements:
            writer.writerow(item)

###################################################################
###################################################################
redo = False
filename2v2 = "top100playersAndGuilds2v2.csv"

guildNamesAndRealm = []
noGuildPlayerNames = []

#get top 100 players and their guilds
if redo is True:
    getAndSavePlayerGuildNames()
with open(filename2v2, "r", newline="", encoding='utf8') as f:
    reader = csv.reader(f)
    next(reader) #skip headings
    for row in reader:
        guildNamesAndRealm.append(row)
        if row[2] == "":
            noGuildPlayerNames.append( [row[0], row[1]] )

#get number of unique guilds
guild_names = []
for player_realm_guild in guildNamesAndRealm:
    if player_realm_guild[2] not in guild_names:
        guild_names.append( player_realm_guild[2] )

# measure guild achievements
redo2 = False
achievementsToFind = [5203, 5241, 5244, 5431, 5429]
guildsWithWantedAchievements = [] #guild_name, real_name, num_achievements_completed
filename2v2guildsFiltered = "guildsWithSearchedAchievements2v2.csv"

if redo2 is True:
    getAndSaveFilteredGuilds()
with open(filename2v2guildsFiltered, "r", newline="", encoding='utf8') as f:
    reader = csv.reader(f)
    next(reader) #skip headings
    for row in reader:
        ids = ast.literal_eval(row[2])
        guildsWithWantedAchievements.append( [row[0], row[1], ids] )

#get number of these top guilds
guild_numTopPlayers = {}
for guild_realm_achievements in guildsWithWantedAchievements:
    if guild_realm_achievements[0] not in guild_numTopPlayers:
        guild_numTopPlayers[ guild_realm_achievements[0] ] = 0
    else:
        guild_numTopPlayers[ guild_realm_achievements[0] ] = guild_numTopPlayers[ guild_realm_achievements[0] ] +1

num_players = []
for info in guild_numTopPlayers:
    num_players.append( guild_numTopPlayers[info] )

average = np.mean(num_players)
max = np.max(num_players)



asdf = 0