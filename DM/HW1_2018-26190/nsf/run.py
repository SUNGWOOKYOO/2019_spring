#!/usr/bin/env python

import sys
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO)

import pydoop
import pydoop.hadut as hadut
import pydoop.test_support as pts


CONF = {
    "mapreduce.job.maps": "2",
    "mapreduce.job.reduces": "2",
    # [TODO] replace student_id with your id, e.g. 2011-12345
    "mapreduce.job.name": "nsf_2018-26190"
}
HADOOP_CONF_DIR = pydoop.hadoop_conf()
PREFIX = os.getenv("PREFIX", pts.get_wd_prefix())


def update_conf(args):
    if args.D:
        for kv_pair in args.D:
            k, v = [_.strip() for _ in kv_pair.split("=")]
            CONF[k] = v


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("pipes_exe", metavar="PIPES_EXE",
                        help="python script to be run by pipes")
    parser.add_argument("local_input", metavar="INPUT_DIR",
                        help="local input directory")
    parser.add_argument("-D", metavar="NAME=VALUE", action="append",
                        help="additional Hadoop configuration parameters")
    return parser


def main(argv):
    parser = make_parser()
    args = parser.parse_args(argv)
    update_conf(args)
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    runner = hadut.PipesRunner(prefix=PREFIX, logger=logger)
    with open(args.pipes_exe) as f:
        pipes_code = pts.adapt_script(f.read())
    runner.set_input(args.local_input, put=True)
    runner.set_exe(pipes_code)
    runner.run(properties=CONF, hadoop_conf_dir=HADOOP_CONF_DIR, logger=logger)
    res = runner.collect_output()
    if not os.getenv("DEBUG"):
        runner.clean()

    with open("results/result_nsf.txt", "w") as f_out:
        f_out.write(res)


if __name__ == "__main__":
    main(sys.argv[1:])
