#!/bin/bash

tab=" --tab-with-profile=Default"
options=(--tab --title=Terminal) 

for subdir in */; do
	gnome-terminal --title="$subdir" -e "bash -c \"cd "$subdir" ; ./runAgent.sh bash\"" &
done

