#!/usr/bin/env python

import os
import optparse
import logging

logging.basicConfig(level=logging.INFO)

import pydoop
import pydoop.test_support as pts
import pydoop.hadut as hadut


HADOOP = pydoop.hadoop_exec()
HADOOP_CONF_DIR = pydoop.hadoop_conf()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.normpath(os.path.join(THIS_DIR, "input"))
LOCAL_DST_SCRIPT = os.path.normpath(os.path.join(THIS_DIR, "bin/dst_count.py"))
LOCAL_FILTER_SCRIPT = os.path.normpath(os.path.join(THIS_DIR, "bin/filter.py"))

MR_JOB_NAME = "mapreduce.job.name"
MR_HOME_DIR = 'mapreduce.admin.user.home.dir'
PIPES_JAVA_RR = "mapreduce.pipes.isjavarecordreader"
PIPES_JAVA_RW = "mapreduce.pipes.isjavarecordwriter"
MR_OUT_COMPRESS_TYPE = "mapreduce.output.fileoutputformat.compression.type"
MR_REDUCE_TASKS = "mapreduce.job.reduces"
MR_IN_CLASS = "mapred.input.format.class"
MR_OUT_CLASS = "mapred.output.format.class"
MRLIB = "org.apache.hadoop.mapred"

BASE_MR_OPTIONS = {
    PIPES_JAVA_RR: "true",
    PIPES_JAVA_RW: "true",
    MR_HOME_DIR: os.path.expanduser("~"),
}

PREFIX = os.getenv("PREFIX", pts.get_wd_prefix())


def make_parser():
    parser = optparse.OptionParser(usage="%prog [OPTIONS]")
    parser.add_option("-i", dest="input", metavar="STRING",
                      help="input dir/file ['%default']",
                      default=DEFAULT_INPUT)
    parser.add_option("-t", type="int", dest="threshold", metavar="INT",
                      help="min word occurrence [%default]", default=10)
    return parser


def run_dst(opt):
    runner = hadut.PipesRunner(prefix=PREFIX)
    options = BASE_MR_OPTIONS.copy()
    options.update({
        # [TODO] replace student_id with your id, e.g. 2011-12345
        MR_JOB_NAME: "dst_count_2018-26190",
        MR_OUT_CLASS: "%s.SequenceFileOutputFormat" % MRLIB,
        MR_OUT_COMPRESS_TYPE: "NONE",
        MR_REDUCE_TASKS: "2",
    })
    with open(LOCAL_DST_SCRIPT) as f:
        pipes_code = pts.adapt_script(f.read())
    runner.set_input(opt.input, put=True)
    runner.set_exe(pipes_code)
    runner.run(properties=options, hadoop_conf_dir=HADOOP_CONF_DIR)
    return runner.output


def run_filter(opt, input_):
    runner = hadut.PipesRunner(prefix=PREFIX)
    options = BASE_MR_OPTIONS.copy()
    options.update({
        # [TODO] replace student_id with your id, e.g. 2011-12345
        MR_JOB_NAME: "filter_2018-26190",
        MR_IN_CLASS: "%s.SequenceFileInputFormat" % MRLIB,
        MR_REDUCE_TASKS: "1",
    })
    with open(LOCAL_FILTER_SCRIPT) as f:
        pipes_code = pts.adapt_script(f.read())
    runner.set_input(input_)
    runner.set_exe(pipes_code)
    runner.run(properties=options, hadoop_conf_dir=HADOOP_CONF_DIR)
    return runner.output


def main():
    parser = make_parser()
    opt, _ = parser.parse_args()
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    logger.info("running dst counter")
    dst_output = run_dst(opt)
    logger.info("running top50 filter")
    filter_output = run_filter(opt, dst_output)
    logger.info("checking results")
    res = hadut.collect_output(filter_output)

    with open("results/result_tf.txt", "w") as f_out:
        f_out.write(res)


if __name__ == "__main__":
    main()
