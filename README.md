# TechScale_Insights
A backend focused CRUD- API Blog application to gain a deeper understanding of scalable strategies like microservices architecture, caching, and load balancing. 



# INSTALLATION INSTRUCTIONS
The moduels needed for this project are all in the requirements.txt file and can be installed with the command:
 ```pip3 install requirements.txt```

Then you need Mysql to be install:
linux:
```sudo apt-get install mysql -y```

Once MySQL is installed it needs to be configured.

NOTE: each service needs its own database, username and password.
# ----------  MySQL Config -----------------------------
# user_service
```CREATE DATABASE Users;```
```CREATE USER 'user_service'@'localhost' IDENTIFIED BY 'us1234'```
```GRANT ALL PRIVILEGES ON Users.* TO 'user_service'@'localhost';```
```FLUSH PRIVILEGES;```

# blog_service
```CREATE DATABASE blog;```
```CREATE USER 'blog_service'@'localhost' IDENTIFIED BY 'bs1234'```
```GRANT ALL PRIVILEGES ON blog.* TO 'blog_service'@'localhost';```
```FLUSH PRIVILEGES;```

# auth_service
```CREATE DATABASE auth;```
```CREATE USER 'auth_service'@'localhost' IDENTIFIED BY 'as1234'```
```GRANT ALL PRIVILEGES ON auth.* TO 'auth_service'@'localhost';```
```FLUSH PRIVILEGES;```
# ----------  End MySQL Config -----------------------------

Each Service Requires its own .env file to be present in its directory and has had an example with everything pre-configured for this MySQL setup.
basically if you use those sql statements to make the databases you can just copy env.example in each folder to ./.env and it should work.

Now each service needs to be run manually, open a fresh terminal in each sub-directory and run:
from app/user_service:
python3 user.py

from app/auth_service:
python3 auth.py

from app/blog_service:
python3 blog_service.py

Once those are running its time for nginx.

save blog.conf in /etc/nginx/sites-available.
then sym-link it to sites-enables
then reload nginx.

Everything should be working, now all you need is a front end.