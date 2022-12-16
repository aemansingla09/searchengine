# Setup Chrome

#Uncomment,If chrome isn't installed
# wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
# sudo sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

sudo apt-get update
sudo apt install google-chrome-stable
google-chrome --version

#Download latest chromedriver
VERSION_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
VERSION=$(curl -f --silent $VERSION_URL)
if [ -z "$VERSION" ]; then
  echo "Failed to read current version from $VERSION_URL. Aborting."
  exit 1
else
  echo "Current version is $VERSION"
fi
# Abort script if any of the next commands fails.
set -e pipefail

ZIPFILEPATH="./userapp/static/crawler/chromedriver-$VERSION.zip"
echo "Downloading to $ZIPFILEPATH"
curl -f --silent "https://chromedriver.storage.googleapis.com/$VERSION/chromedriver_linux64.zip" > "$ZIPFILEPATH"

BINFILEPATH="./userapp/static/crawler/chromedriver/linux_chromedriver-$VERSION"
echo "Extracting to $BINFILEPATH"
unzip -p "$ZIPFILEPATH" chromedriver > "$BINFILEPATH"

echo Setting execute flag
chmod +rwx "$BINFILEPATH"

# echo Updating symlink
# ln -nfs "$BINFILEPATH" ~/bin/chromedriver

echo Removing ZIP file
rm "$ZIPFILEPATH"
echo Done

