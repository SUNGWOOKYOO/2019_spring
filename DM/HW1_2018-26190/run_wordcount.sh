#!/usr/bin/env bash
    
this="${BASH_SOURCE-$0}"
this_dir=$(cd -P -- "$(dirname -- "${this}")" && pwd -P)

container_id=$(sudo docker ps -aqf "name=pydoop")

sudo docker stop ${container_id}
sudo docker rm ${container_id}

sudo docker run -p 8020:8020 --name pydoop -v ${this_dir}:/hw1 -w /hw1 -d crs4/pydoop 

sleep 3

sudo docker exec -it pydoop bash -c ./wordcount/run
