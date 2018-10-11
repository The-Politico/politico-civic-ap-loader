import math
import os
import shutil
import subprocess
import sys

from datetime import datetime
from glob import glob
from time import sleep, time

from django.conf import settings as project_settings
from django.core.management.base import BaseCommand

from aploader.conf import settings as app_settings


class Command(BaseCommand):
    help = "Run the results processing script"

    def main(self, script_args, deploy_script_args, run_once):
        results_start = 0
        i = 0

        if self.test:
            today = datetime.now().strftime("%Y-%m-%d")
            test_path = os.path.join(
                self.output_dir,
                "recordings",
                self.election_date,
                today,
                self.level,
            )
            if not os.path.exists(test_path):
                os.makedirs(test_path)

        if self.replay:
            replay_path = os.path.join(
                self.output_dir,
                "recordings",
                self.election_date,
                self.replay,
                self.level,
            )
            files = glob("{}/*.json".format(replay_path))
            files.sort(key=os.path.getmtime)
            num_files = len(files)
            seconds = int(self.replay_length) * 60
            interval = seconds / num_files
            iteration_speed = 1

            if interval <= 10 and self.level == "state":
                iteration_speed = math.ceil(10 / interval)
                interval = 10

            if interval <= 30 and self.level == "county":
                iteration_speed = math.ceil(30 / interval)
                interval = 30

        else:
            interval = app_settings.RESULTS_DAEMON_INTERVAL

        while True:
            now = time()

            if (now - results_start) > interval:
                results_start = now

                if self.replay:
                    if i < len(files):
                        script_args.extend(["-f", files[i]])
                        print(files[i], i)
                        i += iteration_speed
                    else:
                        print("reached end of test directory, exiting")
                        sys.exit(0)

                subprocess.run(script_args)
                sleep(2)
                subprocess.run(deploy_script_args)

            if run_once:
                print("run once specified, exiting")
                sys.exit(0)

            sleep(1)

    def add_arguments(self, parser):
        parser.add_argument("election_date", type=str)
        parser.add_argument("level", type=str)
        parser.add_argument("--test", dest="test", action="store_true")
        parser.add_argument("--run_once", dest="run_once", action="store_true")
        parser.add_argument("--replay", dest="replay", type=str)
        parser.add_argument("--replay-length", dest="replay_length", type=str)
        parser.add_argument("--zeroes", dest="zeroes", action="store_true")

    def handle(self, *args, **options):
        self.election_date = options["election_date"]
        self.replay = options["replay"]
        self.replay_length = options["replay_length"]
        self.test = options["test"]
        self.zeroes = options["zeroes"]
        self.level = options["level"]

        cmd_path = os.path.dirname(os.path.realpath(__file__))
        bash_script = os.path.join(cmd_path, "../../bin/results.sh")
        deploy_script = os.path.join(cmd_path, "../../bin/deploy.sh")

        self.output_dir = os.path.join(
            project_settings.BASE_DIR, app_settings.RESULTS_STATIC_DIR
        )

        prev_results = os.path.join(
            self.output_dir, "election-results", self.level
        )

        if not os.path.exists(prev_results):
            os.makedirs(prev_results)

        for f in os.listdir(prev_results):
            f_path = os.path.join(prev_results, f)

            try:
                if os.path.isfile(f_path):
                    os.unlink(f_path)
                elif os.path.isdir(f_path):
                    shutil.rmtree(f_path)
            except Exception as e:
                print(e)

        script_args = [
            "bash",
            bash_script,
            "-d",
            self.election_date,
            "-o",
            self.output_dir,
            "-l",
            self.level,
        ]

        if options["test"]:
            script_args.extend(["-t"])

        if options["zeroes"]:
            script_args.extend(["-z"])

        deploy_script_args = [
            "bash",
            deploy_script,
            "-b",
            app_settings.AWS_S3_BUCKET,
            "-l",
            self.level,
            "-o",
            self.output_dir,
        ]

        self.main(script_args, deploy_script_args, options["run_once"])
