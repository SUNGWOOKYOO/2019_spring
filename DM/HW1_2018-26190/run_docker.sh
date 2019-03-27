#!/usr/bin/env bash

this="${BASH_SOURCE-$0}"
this_dir=$(cd -P -- "$(dirname -- "${this}")" && pwd -P)

sudo docker run -p 8020:8020 --name pydoop -v ${this_dir}:/hw1 -w /hw1 -d crs4/pydoop 
