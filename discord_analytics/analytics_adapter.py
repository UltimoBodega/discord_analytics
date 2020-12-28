import pathlib
import subprocess
import json
import time
from collections import defaultdict
from libdisc import colorstr, stats_interface
import progressbar

class Discord_Analytics():
    """
    TODO
    """

    def __init__(self, config_file='config.json', show_top=30):
        self.db = stats_interface.StatsDB()
        self.adapter_path = pathlib.Path(__file__).parent.absolute()
        config_paths = [str(self.adapter_path)+'/'+config_file, config_file]
        self.show_top = show_top
        self.clr = colorstr.bcolors()
        self.last_fetch_timestamp = defaultdict(int)
        self.export_filename = defaultdict(str)
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
        self.token = config_dict["token"]
        self.bot_token = config_dict["bot_token"]
        
    def download_chat_messages(self, channel_id, last_ts):
        """
        Downloads chat messages, once per hour
        """
        append_cmd= ""
        if last_ts is not None:
            append_cmd = ' --after ' +last_ts

        self.export_filename[channel_id] = str(channel_id)+".json"
        self.export_cmd = (self.discord_chat_cli+
                           ' export -f JSON --dateformat "u" -t '+self.token
                           +' -c '+str(channel_id)
                           +' -o '+str(self.adapter_path)+'/'+self.export_filename[channel_id]
                           +append_cmd)

        print(self.export_cmd)

        # if(time.time() - self.last_fetch_timestamp[channel_id] > 3600):
        #     self.last_fetch_timestamp[channel_id] = time.time()
        subprocess.run(self.export_cmd.split())

    def compute_char_stats(self, channel_id):
        """
        Computes chars per user statistics
        """
        output_str = "```"
        char_count = defaultdict(int)
        users = self.db.get_all_users()

        for user in users:
            char_count[user.name] = self.db.sum_user_chars(user.name, channel_id)

        for p, count in sorted(char_count.items(), key=lambda item: item[1], reverse=True):
            if 'bot' in p:
                continue
            output_str = output_str + f"El {p}: {count}" + '\n'

        output_str = output_str + '```'
        return output_str


    def load_db(self, channel_id):
        """
        Loads JSON file into SQLite db

        Extracts and transforms data in the JSON message chat log and
        loads it into a 
        """
        message_file = str(self.adapter_path)+'/'+self.export_filename[channel_id]
        message_dict = json.load(open(message_file))

        len_message = len(message_dict["messages"])
        bar = progressbar.ProgressBar(maxval=len_message, \
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        i=0
        for message in message_dict["messages"]:
            bar.update(i+1)
            i+=1
            timestamp = message['timestamp'].replace("+00:00", "").ljust(23,"0")+"Z"
            self.db.add_new_message(user_name = message['author']['name'],
                                    message_timestamp = timestamp,
                                    message_channel_id = channel_id,
                                    message_words = len(message['content'].split()),
                                    message_chars = len(message['content']))
        bar.finish()