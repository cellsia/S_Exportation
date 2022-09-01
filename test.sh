#!/bin/bash
host=""
public_key=""
private_key=""
project_id=0
software_id=0
image_id=0
offset=0
box_size=0

python3 src/run.py \
    --cytomine_host $host \
    --cytomine_public_key $public_key \
    --cytomine_private_key $private_key \
    --cytomine_id_project $project_id \
    --cytomine_id_software $software_id \
    --image_to_analyze $image_id \
    --offset $offset \
    --box_size $box_size
