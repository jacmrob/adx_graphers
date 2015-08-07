#!/bin/bash

python reach_maker.py "$1"
python adx_grapher.py "$1"
python taut_grapher.py "$1"
# these parameters can be changed to change which graphs 
python concat_graphs.py "$1" "/Percent_received.png" "/Quality.png" "/Reach_graph.png" "/Budget_spent.png"