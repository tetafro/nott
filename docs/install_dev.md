#### 1. Install software
```
sudo apt-get install python3-pip python3-dev gcc
sudo apt-get install libjpeg-dev zlib1g-dev # for Pillow
sudo apt-get install nginx
sudo apt-get install postgresql libpq-dev
sudo apt-get install git
sudo pip3 install virtualenv
```

#### 2. Clone the repository
```
git clone https://github.com/tetafro/notes.git
```

#### 3. Environment variables
```
export SERVER_MODE=dev
sudo sh -c 'echo SERVER_MODE=dev >> /etc/environment'
```

#### 4. Make virtualenv
```
cd notes
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### 6. Copy configs
```
sudo cp configs/nginx/sites-avaliable/notes /etc/nginx/sites-available/

cd /etc/nginx/sites-enabled/
sudo ln -s ../sites-available/notes .
```

#### 7. DB setup
```
sudo su - postgres
createdb db_notes
createuser --no-createdb pguser
psql
\password pguser
GRANT ALL PRIVILEGES ON DATABASE db_notes TO pguser;
\quit

./manage.py migrate
```

#### 8. Run server
```
./manage.py runserver
```