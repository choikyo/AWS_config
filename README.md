# AWS Linux Configuration & Django deployment
IP: 18.217.226.97
If you have already setup your environment, please skip to ***"12. Login as grader"***

## 1. Start AWS Lightsail Instance
- Create an AWS account
- Start a new Ubuntu Linux server instance on Amazon Lightsail
- click bulit-in console and login as the default user "ubuntu"
    
## 2. Update Package
    sudo apt-get update

## 3. Setup Firewall
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 2200/tcp 
    sudo ufw allow 80
    sudo ufw allow 123/udp
    sudo ufw enable
    
## 4. New User grader (sudoer)

    sudo adduser grader
    sudo su -grader
    sudo usermod -aG sudo grader
    
## 5. SSH setting for user grader
Edit sshd_config file

    sudo nano /etc/ssh/sshd_config
    
Open 2200 port by finding below syntax and replace port to 2200

    #What ports, IPs and protocols we listen for
    Port 2200
    
Disable root login by finding PermitRootLogin and replace yes with no

    PermitRootLogin no
    
Generate SSH keys.
Switch to user grader and generate keys
    
    sudo su - grader
    ssh-keygen
    
Leave public key on the server
    
    cd ~/.ssh
    mv id_rsa.pub authorized_keys
    
Move the private key to your local machine, and delete it from server.
***In this project, I have re-named private key as "grader" file. Also, I have setup the "passphrase" as "password" (all lowercase)***

Restart after SSH configueration

    sudo /etc/init.d/ssh restart

## 6. Install Finger Apache2, Python3, Mod-WSGI, Pip3, PostgreSQL
    
    sudo apt-get install finger, apache2 python3 pip3 libapache2-mod-wsgi postgresql    

## 7. Install Flask, Google API, SQLAlchemy
    sudo pip3 install flask
    sudo pip3 install --upgrade oauth2client
    sudo pip3 install sqlalchemy

## 8. Postgresql DB & Data Setup
Create DB user "catalog", and set password

    sudo -u postgres psql postgres
    sudo -u postgres createuser catalog
    \password catalog

In this project, I have setup the password lowercase "password"
Create DB "catalog" and Schema "catalog"

    CREATE DATABASE catalog;
    \connect catalog;
    CREATE SCHEMA catalog;

## 9. Setup Python Code 
Place the entire parent folder "FlaskApp" under the new server's path "/var/www/"

## 10. Sites-Available Configueration
Copy file "AWS_config\site-config\FlaskApp.conf" to the new server's path "/etc/apache2/sites-available" 

You can take down the default app, then bring up Flask

    sudo a2dissite 000-default.conf
    sudo a2ensite FlaskApp.conf

This can be verified under "/etc/apache2/sites-enabled"

## 11 Populate tables and data in Postgres
    cd /var/www/FlaskApp/FlaskApp
    sudo python3 itempopulator.py

## 12. Login as "grader"
Use the private key to login.
File path is "AWS_config/SSH_private/grader"
Passphrase is "password". Refer to file :  "AWS_config/SSH_private/passphrase.txt"

    ssh grader@18.217.226.97 -p 2200 -i grader




    

