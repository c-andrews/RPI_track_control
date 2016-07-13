
path = pwd

# Make the www directory if it doesnt exsist
mkdir -p "/var/www/"

# Copy the app.py file to /home/pi/
cp "${path}/app.py" "/home/pi/"

# Copy the app.html to /var/www/
cp "${path}/app.html" "/var/www/"

# Copy the assets folder to /var/www/
cp -avr "${path}/assets" "/var/www/"