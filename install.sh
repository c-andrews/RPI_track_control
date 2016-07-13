#!/bin/bash

path = pwd

# Make the www directory if it doesnt exsist
echo "Making /var/www/ directory"
mkdir -p "/var/www/"

# Copy the app.py file to /home/pi/
echo "Copying ${path}/app.py to /home/pi/"
cp "${path}/app.py" "/home/pi/"

# Copy the app.html to /var/www/
echo "Copying ${path}/app.html to /var/www/"
cp "${path}/app.html" "/var/www/"

# Copy the assets folder to /var/www/
echo "Copying ${path}/assets to /var/www/"
cp -avr "${path}/assets" "/var/www/"