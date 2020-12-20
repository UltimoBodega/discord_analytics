import pathlib
import subprocess
import json
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import defaultdict
from libdisc import colorstr

class Discord_Analytics():

    def __init__(self, config_file='config.json', show_top=30):
        """
        Initializes class configuration parameters
        """
        self.adapter_path = pathlib.Path(__file__).parent.absolute()
        config_paths = [str(self.adapter_path)+'\\'+config_file, config_file]
        self.show_top = show_top
        self.export_filename = 'chat_messages.html'
        self.clr = colorstr.bcolors()
        self.last_fetch_timestamp = 0
        config_dict = None

        for config_path in config_paths:
            try:
                config_dict = json.load(open(config_path))
                if config_dict:
                    break
            except:
                pass
        if not config_dict:
            print(f"\n{self.clr.FAIL}[ERROR]{self.clr.ENDC} Empty or non-existent config file in either of paths:")
            print(f"{config_paths}")
            return

        self.discord_chat_cli = config_dict["discord_chat_cli"]
        self.channel_id = config_dict["channel_id"]
        self.token = config_dict["token"]
        self.bot_token = config_dict["bot_token"]
        self.export_cmd = self.discord_chat_cli+' export -t '+self.token+' -c '+self.channel_id+' -o '+str(self.adapter_path)+'\\'+self.export_filename

    def download_chat_messages(self):
        """
        Downloads chat messages, once per hour
        """
        if(self.last_fetch_timestamp - time.time() > 3600)
            self.last_fetch_timestamp = time.time()
            subprocess.call(self.export_cmd)

    def compute_chat_analytics(self, plotting=False):
        """
        Computes chat analytics.

        Computes rank of words and characters used by users.
        """

        with open(str(self.adapter_path)+'\\'+self.export_filename, 'r', encoding="utf8") as f:
            contents = f.read()
            soup = BeautifulSoup(contents, 'lxml')
            chatlog = soup.find_all('div', class_='chatlog__messages')
            char_count = defaultdict(int)
            word_dict = defaultdict(int)
            word_counter = defaultdict(int)
            for i in range(len(chatlog)):
                person = chatlog[i].find_all('span', class_='chatlog__author-name')[0].get_text()
                for message in chatlog[i].find_all('span', class_='preserve-whitespace'):
                    char_count[person] = char_count[person] + len(message.get_text())
                    word_dict[person] = word_dict[person] + len(message.get_text().split())
                    for w in message.get_text().split():
                        word_counter[w] += 1

            plt.bar(char_count.keys(), char_count.values(), color='g',label='Character count')
            plt.bar(word_dict.keys(), word_dict.values(), color='r',label='Word count')
            plt.xlabel("Players")
            plt.grid()
            plt.legend()
            
            popular_words = sorted(word_counter, key = word_counter.get, reverse = True)
            tops = popular_words[:self.show_top]

            output_str = ""

            for p, count in sorted(char_count.items(), key=lambda item: item[1], reverse=True):
                if 'bot' in p:
                    continue
                print(f"El {p}: {count}")
                output_str = output_str + f"El {p}: {count}" + '\n'
            for i in range(len(tops)):
                print(f"#{i}: {tops[i]}, ocurrances: {word_counter[tops[i]]}")

            if plotting:
                plt.show()

            return output_str