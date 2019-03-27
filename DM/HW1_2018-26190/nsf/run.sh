#!/usr/bin/env bash

set -euo pipefail
[ -n "${DEBUG:-}" ] && set -x
this="${BASH_SOURCE-$0}"
this_dir=$(cd -P -- "$(dirname -- "${this}")" && pwd -P)
. "${this_dir}/../config.sh"

FULL_OPTS="\
-D mapreduce.pipes.isjavarecordreader=false
-D mapreduce.pipes.isjavarecordwriter=false
-D pydoop.hdfs.user=${USER}"

BIN="${this_dir}"/bin/nsf.py

OPTS="${FULL_OPTS}"

${PYTHON} "${this_dir}"/run.py "${BIN}" "${this_dir}"/input
