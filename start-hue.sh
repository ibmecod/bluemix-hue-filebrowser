#!/bin/bash
# Fixup hue.ini
python /data/install/update-hue-ini.py /data/install/hue-template.ini /usr/local/hue/desktop/conf/hue.ini 

# Start hue if fixup is successful
# If fixup fails output error message and run forever
# so container doesn't crash
if [ $? -eq 0 ]; then
    /usr/local/hue/build/env/bin/hue runserver 0.0.0.0:8000
else
    while true
    do 
       echo "Fatal error discovering service credentials , HUE not started"
       sleep 30
    done
fi




