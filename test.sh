#!/bin/bash
host="https://viewer.cells-ia.com/"
public_key="99e48860-2c41-42fd-9937-2168acb11733"
private_key="0c704ecf-0bd7-4f47-82c6-576f080437a4"
software_id="289476"
project_id="372282"
image_to_analyze="372504"


python3 src/run.py \
    --host $host \
    --public_key $public_key \
    --private_key $private_key \
    --software_id $software_id \
    --project_id $project_id \
    --image_to_analyze $image_to_analyze