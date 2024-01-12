import os
import time
import asyncio
from _babase import env

log_path = os.path.join(env()["python_directory_user"], "logs" + os.sep)
cmd_logs = []


class LoggerControl:
    def __init__(self, msg, account_id, role, player_name):
        self.msg = msg
        self.account_id = account_id
        self.role = role
        self.player_name = player_name

    def log(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{current_time} - AccountID: {self.account_id}, Role: {self.role}, Player: {self.player_name}, Command: {self.msg}\n"
        cmd_logs.append(log_entry)

        if len(cmd_logs) > 3:
            self.write_log(log_path + "cmd.log", cmd_logs)
            cmd_logs.clear()

    def write_log(self, path, data):
        with open(path, "a+", encoding="utf-8") as f:
            f.writelines(data)
