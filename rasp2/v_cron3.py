import datetime
import traceback
import os

import v_mler
import v_liner


class Main:

    def __init__(self):

        try:

            # ログファイル出力先
            log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "log")
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)

            # モジュール読み込み
            self.mler = v_mler.Manager()
            self.liner = v_liner.Manager()

            # 開始
            print("v_cron3.py", datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S"), "(UTC)")

            self.mler.analyze_next()

        except Exception as e:
            self.report_error(traceback.format_exc(), log_dir, self.liner)


    def report_error(self, trace, log_dir, liner):
        print(trace)

        now_datetime = datetime.datetime.now(datetime.timezone.utc)

        # ログファイル
        try:
            log_path = os.path.join(log_dir, "v_cron3_" + now_datetime.strftime("%Y_%m_%d_%H_%M_%S") + ".log")
            with open(log_path, mode = "w", encoding = "utf_8") as log_file:
                log_file.write("ERROR: v_cron3.py " + now_datetime.strftime("%Y/%m/%d %H:%M:%S") + " (UTC)\n" + trace)
        except Exception as e:
            pass

        # LINE
        try:
            self.liner = v_liner.Manager()
            liner.send("ERROR: v_cron3.py " + now_datetime.strftime("%Y/%m/%d %H:%M:%S") + " (UTC)\n" + trace)
        except Exception as e:
            pass


if __name__ == "__main__":
    Main()
