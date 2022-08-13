import requests
import json
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from mysqltw import MySQLTW
import mysql.connector


class Twitch():
    def __init__(self, mysql):
        self.twitchToken = None
        self.mysql = mysql

    def check_token(self):
        try:
            with open('twitch_token.txt', 'r+') as f:
                self.twitchToken = json.load(f)
        except (IOError, JSONDecodeError) as e:
            pass
        if self.expire_token():
            self.generate_token()
        print("Token: ", self.twitchToken['access_token'])

    def expire_token(self):
        if self.twitchToken is None or str(datetime.now()) > self.twitchToken['exp_date']:
            print('Token expired!')
            return True
        else:
            print('Token good, epired in: ', self.twitchToken['exp_date'])
            return False

    def generate_token(self):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': 'tfr9dof3rbstw0sz8al5qeirirfg4m',
            'client_secret': '4kfhrny1rkxemou1to2fsl8fjqz4yu'
        }
        response = requests.post('https://id.twitch.tv/oauth2/token', data=payload)
        if response.status_code != 200:
            print('Error getting token')
        print(response.text)
        self.twitchToken = json.loads(response.text)
        self.twitchToken['exp_date'] = str(datetime.now() + timedelta(seconds=self.twitchToken['expires_in']))
        with open('twitch_token.txt', 'w+') as json_file:
            json.dump(self.twitchToken, json_file)

    def request(self, url):
        if self.check_token():
            self.generate_token()
        headers = CaseInsensitiveDict()
        headers["Client-Id"] = "tfr9dof3rbstw0sz8al5qeirirfg4m"
        headers["Authorization"] = "Bearer "+self.twitchToken['access_token']
        response = requests.get(url, headers=headers)
        return response.text
    
    def twitch_check(self, streamer): #poprawić url zamiast streamer
        print("Check streamer:", streamer)
        response = json.loads(self.request(streamer))
        if not response['data']:
            print("Błąd sprawdzenia")
        else:
            streamer_data = response['data'][0]
            twitch_id = streamer_data['user_id']
            twitch_username = streamer_data['user_name']
            live = streamer_data['type']
            date = twitch_username + " " + live
                
            sql = f"SELECT `twitch_id` FROM `twitch` WHERE `twitch_id` = {twitch_id} LIMIT 1"
            if self.mysql.query(sql).fetchone() == None:
                self.twitch_add(twitch_id, date)


    def twitch_add(self, twitch_id, raw_date):
        sql = "INSERT INTO `twitch` (`twitch_id`, `data`) VALUES (%s, %s)"
        print("Add streamer:", twitch_id)
        val = []
        val.append(twitch_id)
        val.append(raw_date)
        print(sql, val)
        self.mysql.query(sql, val)
        self.mysql.commit()

    def check_live(self):
        print("Sprawdzanie bazy")
        sql = "SELECT `twitch_id` FROM `twitch`"
        myresult = self.mysql.query(sql).fetchall()
        for user_id in myresult:
            new_date = json.loads(self.request(f"https://api.twitch.tv/helix/streams?user_id={user_id[0]}&first=1"))
            if not new_date['data']:
                print("Błąd sprawdzenia")
                live = ""
            else:
                streamer_data = new_date['data'][0]
                live = streamer_data['type']
                sql = f"SELECT `live` FROM `twitch` WHERE `twitch_id` = {user_id[0]} LIMIT 1"
                old_live = self.mysql.query(sql).fetchone()[0]
                if old_live != live:
                    print("User", user_id[0], "ma live!")
                    sql = f"UPDATE `twitch` SET `live` = 'live' WHERE `twitch_id` = {user_id[0]}"
                    self.mysql.query(sql)
                    self.mysql.commit()

                
