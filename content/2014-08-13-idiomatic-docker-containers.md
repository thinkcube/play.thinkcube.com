Title: Development environments in docker containers, the idiomatic way.
Date: 2014-08-13 21:55
Category: docker
Tags: docker, development
Slug: idiomatic-docker-containers-for-dev-env
Author: Chanux

It has been ten months and Docker has moved from 0.6.1 to 1.1.2 since my previous [article](http://play.thinkcube.com/development-environment-on-docker.html) on setting up development environments using docker. Docker has matured and I have learned things better so the previous article feels outdated. And of course always wanted to write a follow up. At thinkcube, we are using docker to easily spin up development environments for quite complex systems (I have been through setting up those on developer laptops. Oh the horrors!). That is apart from using it in a product still in the works. So sharing our experiences will help someone else looking to do it and we'll find out if we are not doing things the best way.

So here goes the guide to putting development environments in docker containers, the idiomatic way.

This guide will not have a strong relationship with the old one that you have to go back and read it first. Anyhow I will refer to the old one at places for the benefit of people who read the old one.

Let's take the same example as before, setting up wordpress. That requires Apache and MySQL. Previously we slapped both Apache and MySQL in the same docker image but the best practice is to separate things in container world. So here's the plan.

- We install Apache in a container and mount the wordpress code from the host machine. This way you can mount your code in to a docker container that has the necessary stuff for the app to run. You can edit the code the way you have always been doing. Also you can reuse the apache container

- We install MySQL in a separate container. Again, you can reuse it.
  
- We would also use the concept called 'data only containers' so we can retain data beyond a container's life time.

Let's juts get straight in to business. We'll start with Apache/PHP container.

```
#DOCKER-VERSION 1.1.2

# Build the image of ubuntu 14.04 LTS
FROM ubuntu:14.04

# Run apt-get update
RUN apt-get -y update

# Install Apache, PHP and stuff
RUN apt-get -y install apache2
RUN apt-get -y install php5 libapache2-mod-php5 php5-mcrypt
RUN apt-get -y install libapache2-mod-auth-mysql php5-mysql

ADD wordpress.conf /etc/apache2/sites-available/
RUN a2dissite 000-default
RUN a2ensite wordpress

# Expose port 80 to the host machine
EXPOSE 80

ENTRYPOINT ["/usr/sbin/apache2ctl"]
CMD ["-D", "FOREGROUND"]
```

So there we've got a Dockerfile building on Ubuntu 14.04 (Trusty Tahr) base. Update apt and install Apache, PHP and stuff needed to connect to a MySQL server. Then we add virtual host file to instruct Apache to run wordpress (Or any PHP code you throw at it). Next we expose port 80, since that's the port Apache would run on. We use apache2ctl as the entrypoint and passing the options to run apache in the foreground using cmd instruction. Using cmd lets us pass different options when we run the container. There is a reason for running Apache in the foreground. That's required for docker container to keep running.

Check the virtual host file that we add in the Dockerfile. We tell Apache to work with the stuff found at /var/www and send logs to standard output. That's gonna be handy later on.

```apache
<VirtualHost *:80>
    DocumentRoot /var/www/

    LogLevel warn
    ErrorLog /dev/stdout
    CustomLog /dev/stdout combined
</VirtualHost>
```

We are ready to build the Apache container.

```console
chanux@nim:~/idiomatic-docker/apache$ ls
Dockerfile  wordpress.conf
```

`sudo docker build -t apache .`

If that ran without errors, we now have our docker image with Apache and PHP ready.

Let's download wordpress, extract it and see running it with our apache container.

`wget http://wordpress.org/latest.tar.gz`

`tar xzf latest.tar.gz`

```console
chanux@nim:~/idiomatic-docker/apache$ ls
apache latest.tar.gz mysql wordpress
```

`sudo docker run -d -v $PWD/wordpress:/var/www -p 8000:80 --name wordpress apache`

Go check '127.0.0.1:8000' on your browser. You should see wordpress complaining about a missing config file. Just go inside the wordpress directory and create the config file as follows.

`cp wp-config-sample.php wp-config.php`

Take a look at the wp-config.php file. Now we need a database, a MySQL database to continue with. So we create a docker container with MySQL in it. Check the following Dockerfile.

```
FROM ubuntu:14.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-client mysql-server

VOLUME ["/data"]

ADD my.cnf /etc/mysql/conf.d/my.cnf
ADD run.sh /run.sh
RUN chmod +x run.sh

EXPOSE 3306

ENTRYPOINT ["/run.sh"]
```

Except from the familiar stuff at the top we install MySQL there. The DEBIAN_FRONTEND=noninteractive trickery is setting the environment variable so the system knows there's no one who can interact with it. The VOLUME instruction makes a volume that will be mounted as /data in the container. With that we can preserve data between docker restarts. We are adding my.cnf with content you can see below so that we can connect to the MySQL server from outside.

Next is the run script which packs some action and we will look in to soon. MySQL runs on port 3306 by default so we open it up with EXPOSE instruction.The last instruction tells docker to execute our run script when we run the docker image. Normal day so far. Now to check the run script.

```bash
#!/bin/bash

if [ ! -d /data/mysql ]; then
    #setup mysqldb
    mysql_install_db --datadir=/data/mysql
    echo "=> Starting MySQL."
    /usr/bin/mysqld_safe --datadir=/data/mysql > /dev/null 2>&1 &

    RET=1
    while [[ $RET -ne 0 ]]; do
        echo "=> Waiting for confirmation of MySQL service startup"
        sleep 5
        mysql -uroot -e "status" > /dev/null 2>&1
        RET=$?
    done

    PASS='admin123'
    echo "=> Creating MySQL user."
    mysql -uroot -e "CREATE USER 'admin'@'%' IDENTIFIED BY '$PASS'"
    mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION"

    echo "=> Shutting down after setup."
    mysqladmin -uroot shutdown
else
    echo "=> continuing with an existsing mysql setup"
fi

echo "=> Running MySQL Server"
exec mysqld_safe --datadir=/data/mysql
```

As I mentioned before, this will run when we run the docker container. It will check for /data/mysql dir and if it's not present, it'll setup the database assuming it's a fresh run. Otherwise it'll continue since there should be a DB already setup. The script creates a user called admin with admin123 as the password.

MySQL by default places it's data in /var/lib/mysql. We are forcing the installer to use /data/mysql instead. There is something important about /data/mysql directory that you will find out later.

And here is the my.cnf file.

```
[mysqld]
bind-address=0.0.0.0
```

Create the Dockerfile and the run script. You are ready to build the mysql docker image.

```console
chanux@nim:~/idiomatic-docker/mysql$ ls
Dockerfile  my.cnf  run.sh
```

Now run following to build the mysql image

`sudo docker build -t mysql .`

If everything went well you can now run the mysql image. But before doing that we should run a 'data only container'. So that we can retain data beyond a container's life time. Remember? Good!

We are going to retain chosen data in our docker containers and we need a place for that. I would prefer a directory called data in my home directory. And I would prefer it being hidden. So here goes.

`mkdir ~/.data`

And then we run our data only container.

`sudo docker run -d -v ~/.data:/data --name data ubuntu:14.04 true`

With -d we tell docker to run our container in detached mode. Option -v mounts the ~/.data directory we just created inside the data only container. The container is appropriately named as data and we use ubuntu:14.04 since we have already pulled that base image when we built the mysql image. Now we have ourselves a data only container. Time to get on with our mysql container.

`sudo docker run -d --volumes-from data --name mysql mysql`

There we did something special with --volumes-from option. We instructed the mysql container to use volumes from a container called data. Yes, that is our data only container. What really happens is our ~/.data directory shows up at /data inside our mysql container. The run script creates mysql database there so even if we delete the container, the data will be there. If you were paying attention, this is why I said that there is something important about /data/mysql :).

You can see whether the mysql container is running with `sudo docker ps`. Also you can see what was going on in the container with `sudo docker log -f mysql`. What you see are the messages printed by the run and setup scripts. Press `Ctrl+C` to get out of that.

Strangely, you don't see the data container running. That's alright. It doesn't have to be running. You can see that the container is there by running `sudo docker ps -a`

You can try connecting to the mysql server in the container using.. well.. another container.. of the same image :D.

This is how you do it..

`sudo docker run -i -t --link mysql:db --entrypoint="mysql" mysql -u admin -p -h db`

Enter admin123 as the password and you'll get a mysql prompt. Let's now create a database called 'wordpress'. We passed two options to docker run command there. First --link. We will discuss link magic later. Next is --entrypoint. In the mysql Dockerfile we mentioned run.sh as the ENTRYPOINT so that it'll run when the container runs. What we are doing here is making mysql binary run instead of 'run.sh' or in other words, the default entrypoint.

Entrypoint option also comes handy when you want to troubleshoot/look inside containers. You can use bash as the entrypoint and get inside. For example try..

`sudo docker run -i -t --entrypoint="bash" mysql -i` 

..and you will get a console to the container. This is very useful when you want to troubleshoot containers.

```console
mysql> create database wordpress
Query OK, 1 row affected (0.02 sec)
```

Yeah didn't take a tenth of a second ;)

Now we have a MySQL database running and the information needed by wp-config.php file. Go add the details to the file. Following are what you have to change.

```php
define('DB_NAME', 'wordpress');
define('DB_USER', 'admin');
define('DB_PASSWORD', 'admin123');
define('DB_HOST', 'localhost'); #<-- watchout!
```

Wait.. we can't refer to the mysql db as localhost right? We don't have a mysql server running inside Apache container. Looks like all our efforts are in vain. Except we are still perfectly OK. We can do two things here.

1. Find the IP for mysql container and put that as DB_HOST. (For that you can just run `sudo docker inspect --format="{{.NetworkSettings.IPAddress}}" mysql` and get the IP.)

2. Magic

Magic you already know! And that is container linking. You did that when you ran a container to connect to mysql. Go check again. You linked mysql container under the alias db (--link mysql:db) and passed it to mysql as host (-h mysql) option. Magic right? We can do that because when we link a container with another, the linked container information goes in the /etc/hosts file of linking container.

So let's just link mysql with apache container. For that we need to stop the apache container we ran under the name wordress and remove it.

`sudo docker stop wordpress`

`sudo docker rm wordpress`

Now run the container again, this time linking mysql.

`sudo docker run -d -v $PWD/wordpress:/var/www --link mysql:db -p 8000:80 --name wordpress apache`

Update wp-config.php with db instead of localhost as DB_HOST setting.

```php
define('DB_HOST', 'db'); #<-- now we are good!
```

Save the file and go refresh the wordpress page. You will be greeted with wordpress installation page. I hope you can take it from there by yourself.

Logs are very important when you are developing an app. You can see the apache logs with `sudo docker logs -f wordpress`. I told you, forwarding logs to stdout is gonna be handy!. The mysql image is not set up to give convenient access to logs. You can mount a directory from the host to have the logs there (just like you mount you logs, mount a local directory on /var/log/mysql).

You can stop/start the containers as well. You have to use the docker ID or the name you provide to the container.

`sudo docker stop wordpress`

`sudo docker start wordpress`

However docker will do stop/starting the containers when you shutdown/restart the host machine so you don't have to worry about that.

Whew! That was actually a lot. So take your time and try to read extra on concepts that are not clear for you. If you need help you can always hop on the freenode [#docker](http://play.thinkcube.com/webchat.freenode.net/?channels=#docker&nick=) channel and ask the awesome folk there.

To repeat myself, the docker images we created here are reusable. As in when you want mysql and/or apache, you can fire up those images and just start working. Of course you can use the mysql container (link the container with) multiple apps, create different DBs and use it like you'd use any other mysql server. Anyhow it's more docker-y to run different containers for different apps.

Please note that I have made the containers to be super simple so you may need to tweak things a bit for more serious needs. There are other useful docker images on [docker registry](https://registry.hub.docker.com) (That's where we pulled our ubuntu:14.04 base image from). So check there first when you want something.

So that's it. I hope you feel like this!

![I KNOW DOCKER MEME](/images/2WxWmAh.jpg)

I should thank [@laktek](http://twitter.com/laktek), [@vpj](http://twitter.com/vpj) and eljrax, wblankenship_ on #docker freenode channel for the feedback.
