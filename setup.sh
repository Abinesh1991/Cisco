set -x
set -e
apt-get install -y mongodb-org
sudo service mongod start
sudo pip install pymongo
mongorestore urlinfo/urlinfo
python urlinfo/run.py &
