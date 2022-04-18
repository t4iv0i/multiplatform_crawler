# MULTIPLATFORM CRAWLER
### 1. Description
Fields can be collected:
+ Name
+ Username
+ Id
+ Follower
+ Following
+ Description
+ Article
+ ...

Extra Function:
+ Verify channel by hashtag
+ Verify channel by num of follower

Supported Platforms:
+ Facebook
+ Instagram
+ Tiktok
+ Youtube

### 2. Requirements
```
$ sudo apt install python3.9 python3.9-venv
$ python3.9 -m pip install virtualenv
```
### 3. Deploy

#### Install environment
```
$ cd at-cdp-multiplatform-crawler
$ python3.9 -m virtualenv venv
$ ./venv/bin/pip3 install -r requirements.txt
$ sudo dpkg -i google-chrome-stable_current_amd64.deb
$ unzip chromedriver_linux64.zip
```
#### Supervisorctl
**File** /etc/supervisor/conf.d/at-cdp-multiplatform-crawler.conf

```
[program:at-cdp-multiplatform-crawler]
directory=/var/lib/jenkins/workspace/at-cdp-multiplatform-crawler
command=/var/lib/jenkins/workspace/at-cdp-multiplatform-crawler/venv/bin/gunicorn -b 0.0.0.0:58993 main:app --workers 1 --worker-connections 10  --timeout 6000 --worker-class gevent
# kill all sub process  
stopasgroup=true 
# auto start 
autostart=true 
# logging 
stderr_logfile=/var/log/at-cdp-multiplatform-crawler.err.log
stdout_logfile=/var/log/at-cdp-multiplatform-crawler.out.log

```
