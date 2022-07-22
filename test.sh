#!/bin/bash
host=""
public_key=""
private_key=""
software_id=""
project_id=""
image_to_analyze=""


python3 run.py \
    --host $host \
    --public_key $public_key \
    --private_key $private_key \
    --software_id $software_id \
    --project_id $project_id \
    --image_to_analyze $image_to_analyze