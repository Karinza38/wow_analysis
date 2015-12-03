
import requests
import csv
import os.path

guildBook = {}

def collectGuildNamesPVP():
    # method 1: aggregate through pvp leaderboard
    for battleType in [ "2v2", "3v3", "5v5" ]:
        r = requests.get("https://us.api.battle.net/wow/leaderboard/"+battleType+"?locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
        result = r.json()
        for row in result["rows"]:
            if len(guildBook) >= 500:
                break;
            lookupPlayer = [ row["name"], row["realmName"] ]
            r = requests.get("https://us.api.battle.net/wow/character/"+lookupPlayer[1]+"/"+lookupPlayer[0]+
                         "?fields=guild&locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
            result = r.json()
            if "guild" in result:
                guildBook[ result["guild"]["name"] ] = lookupPlayer[1] #save (guildName, realmName)

    #write to csv file
    filename = "fp_guildnames_pvp.csv"
    with open(filename, "w", newline="", encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['guild_name', 'realm_name'])
        for key, value in guildBook.items():
            writer.writerow( [key, value] )

def scrapePVEGuilds( realmNames ):
    for realmName in realmNames:
        r = requests.get("https://us.api.battle.net/wow/challenge/"+realmName+"?locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
        result = r.json()
        for row in result["challenge"]:
            for group in row["groups"]:
                for member in group["members"]:
                    if len(guildBook) >= 500:
                        return
                    if "character" in member and "guild" in member["character"]:
                        guildBook[ member["character"]["guild"] ] = member["character"]["realm"] #save (guildName, realmName)

def collectGuildNamesPVE():
    #1. collect realm names
    r = requests.get("https://us.api.battle.net/wow/realm/status?locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
    result = r.json()
    realmNames = []
    for row in result["realms"]:
        realmNames.append( row["name"] )

    #2. search through challenge API
    scrapePVEGuilds( realmNames )

    #write to csv file
    filename = "fp_guildnames_pve.csv"
    with open(filename, "w", newline="", encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['guild_name', 'realm_name'])
        for key, value in guildBook.items():
            writer.writerow( [key, value] )

def collectGuildNames():
    #collectGuildNamesPVP()
    #collectGuildNamesPVE()

    guildNamesPVP = {}
    guildNamesPVE = {}

    filename = "fp_guildnames_pvp.csv"
    with open(filename, newline="", encoding='utf8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            guildNamesPVP[ row[0] ] = row[1]
            #if len(guildNamesPVP) >= 2:
            #    break

    filename = "fp_guildnames_pve.csv"
    with open(filename, newline="", encoding='utf8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            guildNamesPVE[ row[0] ] = row[1]

    # find common guilds in both PVE and PVP => filter out
    keys_a = set(guildNamesPVP.keys())
    keys_b = set(guildNamesPVE.keys())
    intersection = keys_a & keys_b # '&' operator is used for set intersection

    for k in intersection:
        guildNamesPVP.pop(k, None)
        guildNamesPVE.pop(k, None)

    ##############################################
    getPlayerAchievementsAndGuilds("fp_player_ach_guild_pvp.csv", guildNamesPVP)
    getPlayerAchievementsAndGuilds("fp_player_ach_guild_pve.csv", guildNamesPVE)

    #getPlayerAcheivementsOfGuilds( "fp_guildnames_ach_pvp.csv", guildNamesPVP )
    #getPlayerAcheivementsOfGuilds( "fp_guildnames_ach_pve.csv", guildNamesPVE )

    #perhaps I should be filtering out intersections again

def getPlayerAchievementsAndGuilds( filename, guildNamesAndRealms ):
    ############################################
    doneWithGuilds = set()

    create = False
    if not os.path.isfile(filename):
        create = True
    else:
        # gather already done guilds
        with open(filename, newline="", encoding='utf8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                doneWithGuilds.add( row[2] )

    f = open(filename, "a", newline="", encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    if create is True:
        writer.writerow(['player_name', 'realm_name', "guild_name", "achievements"])
        f.close()

    ############################################
    # for each guild, get all achievements from all players
    i = 0
    for guildName, realmName in guildNamesAndRealms.items():
        i += 1
        if i <= 50:
            continue
        if guildName in doneWithGuilds:
            continue

        result = requests.get("https://us.api.battle.net/wow/guild/"+realmName+"/"+guildName+
                         "?fields=members&locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848").json()
        totMembers = 0
        achievements = {}
        if "members" in result:
            totMembers = len( result["members"] )
            membersCounted = 0
            for member in result["members"]:
                charName = member["character"]["name"]
                result = requests.get("https://us.api.battle.net/wow/character/"+realmName+"/"+charName+
                             "?fields=achievements&locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848").json()
                if "achievements" in result and "achievementsCompleted" in result["achievements"]:
                    #append row to csv
                    f = open(filename, "a", newline="", encoding='utf8')
                    writer = csv.writer(f, delimiter=',')
                    writer.writerow( [charName, realmName, guildName, list(result["achievements"]["achievementsCompleted"])] )
                    f.close()
                    membersCounted += 1
                if membersCounted >= 150: #max member count:150
                    break

        #finished with current guild: add to set
        doneWithGuilds.add( guildName )
        if i >= 151: #max guild count:50
            break
    asdf = 0

def getNonFavouarableGuilds():
    asdf = 0

def getFavourableGuilds():
    # achievements; need to define guilds
    # note) player achievements and guild achievements are different

    # note) then just use guild members instead?

    # note) need to define what is "more favourable" (direction) to who (target)
    # ex. need to define who aligns with what vs who clashes with what
    asdf = 0

def start():
    collectGuildNames()
    return

    r = requests.get("https://us.api.battle.net/wow/data/character/achievements?locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
    result = r.json()

    #1. Analyse player
    lookupPlayer = [ "FellSilent", "Rivendare" ]
    r = requests.get("https://us.api.battle.net/wow/character/"+lookupPlayer[1]+"/"+lookupPlayer[0]+
                     "?fields=guild,achievements,pets,mounts,quests,statistics&locale=en_US&apikey=psc5myk6fxjckujqnqz3anfcqsh2s848")
    result = r.json()

    asdf = 0
    #statistics: pet battles, deaths, quests( total quest complete, daily quests completed )

    playerInfo = result
    #level
    #guild
    #class
    #faction
    #gender
    #name
    #race
    #totalHonorableKills
    #achievementPoints
    playerGuild = result["guild"]

start()
