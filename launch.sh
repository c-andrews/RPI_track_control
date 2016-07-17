#!/bin/sh
#launch.sh

# Start the VNC Server
vncserver :1 -geometry 800x600 -depth 16 -pixelformat rgb565

# Navigate to the root directory
cd /

# Navigate to this directory
cd home/pi/Documents/RPI_track_control

# Run the python script
sudo python app.py

# Navigate back to the root directory
cd /