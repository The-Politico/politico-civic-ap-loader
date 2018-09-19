import os
import shutil
import subprocess
import sys
from time import sleep, time

from django.conf import settings as project_settings
from django.core.management.base import BaseCommand

from aploader.conf import settings as app_settings


class Command(BaseCommand):
    help = "Run the results processing script"

    def main(self, script_args, run_once):
        results_start = 0
        i = 0

        while True:
            now = time()

            if (now - results_start) > app_settings.RESULTS_DAEMON_INTERVAL:
                results_start = now

                test_path = os.path.join(
                    self.output_dir, "recordings", self.election_date
                )
                if not os.path.exists(test_path):
                    os.makedirs(test_path)

                if self.replay:
                    files = os.listdir(test_path)
                    if i < len(files):
                        file = "{0}/{1}".format(test_path, files[i])
                        script_args.extend(["-f", file])
                        print(file, i)
                        i += 2
                    else:
                        print("reached end of test directory, exiting")
                        sys.exit(0)

                subprocess.run(script_args)

            if run_once:
                print("run once specified, exiting")
                sys.exit(0)

            sleep(1)

    def add_arguments(self, parser):
        parser.add_argument("election_date", type=str)
        parser.add_argument("level", type=str)
        parser.add_argument("--test", dest="test", action="store_true")
        parser.add_argument("--run_once", dest="run_once", action="store_true")
        parser.add_argument("--replay", dest="replay", action="store_true")
        parser.add_argument("--zeroes", dest="zeroes", action="store_true")

    def handle(self, *args, **options):
        self.election_date = options["election_date"]
        self.replay = options["replay"]
        self.test = options["test"]
        self.zeroes = options["zeroes"]
        self.level = options["level"]

        cmd_path = os.path.dirname(os.path.realpath(__file__))
        bash_script = os.path.join(cmd_path, "../../bin/results.sh")

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
            "-b",
            app_settings.AWS_S3_BUCKET,
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

        self.main(script_args, options["run_once"])
