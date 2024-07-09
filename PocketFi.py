import os
import sys
import time
import requests
from colorama import *
from datetime import datetime
from urllib.parse import unquote

red = Fore.LIGHTRED_EX
yellow = Fore.LIGHTYELLOW_EX
green = Fore.LIGHTGREEN_EX
black = Fore.LIGHTBLACK_EX
blue = Fore.LIGHTBLUE_EX
white = Fore.LIGHTWHITE_EX
reset = Style.RESET_ALL


class PocketFi:
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "rubot.pocketfi.org",
            "Origin": "https://pocketfi.app",
            "Referer": "https://pocketfi.app/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24", "Microsoft Edge WebView2";v="125"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        
    def next_claim_is(self, last_claim):
        next_claim = last_claim + 3600
        now = datetime.now().timestamp()
        tetod = round(next_claim - now)
        return tetod

    def http(self, url, headers, data=None):
        while True:
            try:
                if data is None:
                    res = requests.get(url, headers=headers)
                    open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
                    if "<html>" in res.text:
                        self.log(f'{red}failed to fetch json response !')
                        time.sleep(2)
                        continue
                    return res

                if data == "":
                    res = requests.post(url, headers=headers)
                    open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
                    if "<html>" in res.text:
                        self.log(f'{red}failed to fetch json response !')
                        time.sleep(2)
                        continue
                    return res

                res = requests.post(url, headers=headers, data=data)
                open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
                if "<html>" in res.text:
                    self.log(f'{red}failed to fetch json response !')
                    time.sleep(2)
                    continue
                return res

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                self.log(f"{red}Connection error")
                time.sleep(1)
                continue

    def countdown(self, t):
        while t:
            minute, second = divmod(t, 60)
            hour, minute = divmod(minute, 60)
            hour = str(hour).zfill(2)
            minute = str(minute).zfill(2)
            second = str(second).zfill(2)
            print(f"{white}Waiting until {hour}:{minute}:{second} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{reset}{msg}")

    def get_user_mining(self, tg_data):
        url = "https://rubot.pocketfi.org/mining/getUserMining"
        url_claim = "https://rubot.pocketfi.org/mining/claimMining"
        headers = self.headers.copy()
        headers["telegramRawData"] = tg_data
        res = self.http(url, headers)
        if len(res.text) <= 0:
            self.log(f"{red}failed get resopnse, 0 length response !")
            return 60
        balance = res.json()["userMining"]["gotAmount"]
        last_claim = res.json()["userMining"]["dttmLastClaim"] / 1000
        self.log(f"{Style.BRIGHT}{Fore.MAGENTA}Balance : {Fore.WHITE}{balance}{Style.RESET_ALL}")
        can_claim = self.next_claim_is(last_claim)
        if can_claim >= 0:
            self.log(f"{Style.BRIGHT}{Fore.RED}Not time to claim !{Style.RESET_ALL}")
        else:
            res = self.http(url_claim, headers, "")
            if len(res.text) <= 0:
                self.log(f"{red}failed get response, 0 length response !")
                return 60
            new_balance = res.json()["userMining"]["gotAmount"]
            self.log(f"{Style.BRIGHT}{Fore.GREEN}Balance after claim : {new_balance}{Style.RESET_ALL}")

        # Claim daily boost after checking/claiming balance
        self.task_executing(headers)
        self.activate_daily_boost(headers)
        
        return 3600

    def task_executing(self, headers):
        url = "https://rubot.pocketfi.org/mining/taskExecuting"
        res = self.http(url, headers)
        if len(res.text) <= 0:
            self.log(f"{red}failed to fetch task executing response !")
        else:
            self.log(f"\033[1;93mTask executing fetched successfully\033[0m")

    def activate_daily_boost(self, headers):
        url = "https://rubot.pocketfi.org/boost/activateDailyBoost"
        res = self.http(url, headers, "")
        if len(res.text) <= 0:
            self.log(f"{red}failed to activate daily boost !")
        else:
            self.log(f"{Style.BRIGHT}{Fore.GREEN}Daily boost activated successfully{Style.RESET_ALL}")

    def main(self):
        banner = "\033[1;91m" + r"""  
  ___    _                  _     
 (  _`\ (_ )               ( )    
 | (_) ) | |    _ _    ___ | |/') 
 |  _ <' | |  /'_` ) /'___)| , <  
 | (_) ) | | ( (_| |( (___ | |\`\ 
 (____/'(___)`\__,_)`\____)(_) (_)
""" + "\033[0m" + "\033[1;92m" + r"""  
  ___                                     
 (  _`\                                   
 | | ) | _ __    _ _    __     _     ___  
 | | | )( '__) /'_` ) /'_ `\ /'_`\ /' _ `\
 | |_) || |   ( (_| |( (_) |( (_) )| ( ) |
 (____/'(_)   `\__,_)`\____)(_) (_) (_) (_)
                     ( )_) |              
                      \___/'              
""" + "\033[0m" + "\033[1;93m" + r"""  
  _   _                _                  
 ( ) ( )              ( )                 
 | |_| |   _ _    ___ | |/')    __   _ __ 
 |  _  | /'_` ) /'___)| , <   /'__`\( '__)
 | | | |( (_| |( (___ | |\`\ (  ___/| |   
 (_) (_)`\__,_)`\____)(_) (_)`\____)(_)   
""" + "\033[0m"
        banner2 = "\033[1;96m----------------------------------\033[0m"
        banner3 = "\033[1;93mScript created by: Black Dragon Hacker\033[0m"
        banner4 = "\033[1;92mJoin Telegram: \nhttps://t.me/BlackDragonHacker007\033[0m"
        banner5 = "\033[1;91mVisit my GitHub: \nhttps://github.com/BlackDragonHacker\033[0m"
        banner6 = "\033[1;96m----------------------------------\033[0m"
        banner7 = "\033[1;38;2;139;69;19;48;2;173;216;230m--------[PocketFi Bot]--------\033[0m"
        banner8 = "\033[1;96m----------------------------------\033[0m"
        arg = sys.argv
        if "marinkitagawa" not in arg:
            os.system("cls" if os.name == "nt" else "clear")
        print(banner)
        print(banner2)
        print(banner3)
        print(banner4)
        print(banner5)
        print(banner6)
        print(banner7)
        print(banner8)
        datas = open("data.txt", "r").read().splitlines()
        if len(datas) <= 0:
            self.log(f"{red}add data account in data.txt first !")
            sys.exit()
        self.log(f"\033[1;96mTotal Accounts: \033[1;97m{len(datas)}")
        while True:
            list_countdown = []
            _start = int(time.time())
            for no, data in enumerate(datas):
                self.log(f"{Style.BRIGHT}{Fore.YELLOW}------Account {no + 1}------")
                res = self.get_user_mining(data)
                list_countdown.append(res)
                self.countdown(5)
            _end = int(time.time())
            _tot = _end - _start
            _min = min(list_countdown)

            if (_min - _tot) <= 0:
                continue

            self.countdown(_min - _tot)


if __name__ == "__main__":
    try:
        PocketFi().main()
    except KeyboardInterrupt:
        sys.exit()
