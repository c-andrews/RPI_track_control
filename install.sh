#!/bin/bash

path = pwd

echo "Current Dir: "+ pwd

# Make the www directory if it doesnt exsist
echo "Making /var/www/ directory"
mkdir -p "/var/www/"

# Copy the app.py file to /home/pi/
echo "Copying app.py to /home/pi/"
cp "app.py" "/home/pi/"

# Copy the app.html to /var/www/
echo "Copying app.html to /var/www/"
cp "app.html" "/var/www/"

# Copy the assets folder to /var/www/
echo "Copying assets to /var/www/"
cp -avr "assets" "/var/www/"