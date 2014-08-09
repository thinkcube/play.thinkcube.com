Title: How to put your development environment on docker? 
Date: 2013-10-18 10:20
Category: docker
Tags: docker, development
Slug: development-environment-on-docker
Author: Chanux
Summary: Step by step guide for setting up a dev environment with docker

What is docker?

“An open source project to pack, ship and run any application as a lightweight container”

That’s right, Docker allows you to run any application in an isolated environment called a container. Docker utilizes LXC, short for Linux containers, to create containers. Setting up LXC and doing useful things with it is a bit of a work. That’s where Docker comes in to help. You can put your application in a Docker container with all it’s configurations and settings in place, add in the databases the app needs and a firewall if you may.Oh and it will handle the networking stuff for you as well. One bad thing though. It takes away your excuse to go back to your favorite time wasting website because… boy it starts in a jiffy. At least it doesn’t slow your computer to a crawl.

Docker is still new and people are doing a lot of amazing things with it and also discovering new ways to use it ever so often. When you start working with Docker you quickly realize it’s an awesome tool to automate your development environment. You may have tried automation scripts, Virtual machines and whatnot for automating your development environment but I’m sure Docker is gonna impress you so easily.

If Docker is that good why do we waste time just talking about it? Exactly. Let’s go Dockerize some development environments.

To keep things simple and to keep difficulty level to a minimum, I am demonstrating how to set up famous LAMP stack on docker so you can do your web development with it. I’m using Ubuntu 13.04 (Raring Ringtail) because it’s what I primarily use and Ubuntu is recommended by Docker developers.

First you need to install Docker. OK I think that instruction is a bit too obvious.

You are better off following the [official guide](https://docs.docker.com/installation/#installation). I’d just list down the steps for completeness.

Docker needs Linux kernel 3.8 and AUFS support. Since Ubuntu Rringtail comes with 3.8 kernel, we only need to install AUFS support (If you are using a previous version of Ubuntu please follow the guide I linked above. If you are not sure check your kernel version with ‘uname -r’)

```
sudo apt-get update
sudo apt-get install linux-image-extra-`uname -r`
```              

Then we add Docker repository key, add Docker repository to our repository list and finally install Docker.

```
wget -qO http://get.docker.io/gpg | sudo apt-key add -
echo “deb https://get.docker.io/ubuntu docker main” | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install lxc-docker
```

Docker is ready for your service. Try running

```
sudo docker run ubuntu:precise /bin/echo Hello World
```

That will take some time because it will have to pull (download) the Ubuntu Precise Pangolin image from Docker index servers. If all is well you’ll see “Hello World” printed. Nothing to celebrate but chances are your programming career started from a Hello World too!

Now that you’ve seen hello world printing on screen you should be feeling like going on some adventures. Let’s sail matey!

I am going to take a different route than many of the Docker tutorials available because you are less likely to find gems in well traveled paths. So we start from writing a ‘Dockerfile’. Then we build our image from it. Familiar stuff for a programmer right?. Launch the editor you hate most and write down the instruction I describe below each on it’s own line in your Dockerfile.

We will build our image from ubuntu 12.04 LTS (precise pangolin). So the first line of the Dockerfile will be

__from ubuntu:precise__

Remember when we first ran Docker to see hello world? Check that command again. We used ubuntu:precise there as well. Docker will have the downloaded image saved so when you build the Dockerfile, it doesn’t have to be downloaded again. Likewise Docker caches things so the subsequent builds are faster. Think about Docker build process as starting an OS image (ubuntu:precise as we’ve instructed above) and running commands on it. So now we have to instruct it to run things. We will run an apt-get update first.

__run apt-get update__

Now we can install things. Let’s just install LAMP with one command, because we can’t be bothered to find out all bits and pieces to get LAMP ready.

__run apt-get -y install lamp-server^__

There are cases we need to put files inside the container. For example I have this little shell script called abracadabra which helps starting the services in our container. Following instruction will put the file called abracadabra inside /usr/local/bin directory of our container. (I assume the file abracadabra is there with the Dockerfile in working directory)

__add abracadabra /usr/local/bin/abracadabra__

We have discussed the essential instructions we are going to use today. It would be boring to go on like this for the rest of the command so lo and behold, the complete Dockerfile.

File: [Dockerfile](https://gist.github.com/chanux/6610593#file-dockerfile)

```
#DOCKER-VERSION 0.6.1

# Build the image of ubuntu 12.04 LTS
from ubuntu:precise

# Run apt-get update
run apt-get -y update

# Install LAMP
run DEBIAN_FRONTEND=noninteractive apt-get -y install lamp-server^
run apt-get -y install vim-tiny

# Put custom scripts in the container and give proper permissions to them
add abracadabra /usr/local/bin/abracadabra
run chmod 755 /usr/local/bin/abracadabra

add wordpress.vhost /etc/apache2/sites-available/wordpress
run a2ensite wordpress

# Expose port 80 to the host machine
expose 80
```

Now let us checkout what magic is behind abracadabra script

File: [abracadabra](https://gist.github.com/chanux/6610593#file-wordpress-vhost)

```
#!/bin/bash

a2dissite default
apache2ctl graceful
/usr/bin/mysqld_safe &
```

Nothing much. We are just starting Apache and mysql there.

The last piece is the virtual host (vhost for short) for the wordpress. A complete explanation about vhosts is out of the scope of this article but I created a separate vhost and kept it really simple so someone new to this can also pick it up.

File: [wordpress.vhost](https://gist.github.com/chanux/6610593#file-wordpress-vhost)

```
<VirtualHost *:80>

    ServerAdmin webmaster@localhost

    DocumentRoot /var/www/wordpress
    <Directory /var/www/wordpress/> 
        Options Indexes FollowSymLinks MultiViews
        AllowOverride None 
        Order allow,deny allow from all 
    </Directory>

    # Possible values include: debug, info, notice, warn, error, crit, # alert, emerg.
    LogLevel warn ErrorLog ${APACHE_LOG_DIR}/error.log

    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Now we are ready to build. Put all the files I mentioned above in one directory and cd in to it. Create two directories called mysql and www. We are going to need those later.

```
chanux@nim:~/docker-lamp$ mkdir mysql www
```

Recheck whether you have everything needed for our adventure.

```
chanux@nim:~/docker-lamp$ ls
abracadabra Dockerfile mysql wordpress.vhost www
```

Let’s run the docker build command.

```
chanux@nim:~/docker-lamp$ sudo docker build -t mylamp . # Do not miss that dot at the end of the command
```

‘docker build’ command will look for the Dockerfile (capital D) and follow the instructions in it to build our shiny new image. It will take a bit of time because we told Docker to apt-get update and install lamp. When our image is finally ready we can just run it calling it by the name (tag) we set for it, ‘mylamp’.

Before moving to more interesting stuff we need to get one dirty task done. I wouldn’t go in to details about this right now but you’ll understand what it’s about when I describe the docker run command.

```
chanux@nim:~/docker-lamp$ sudo docker run -d -v $(pwd)/mysql:/tmp/mysql uwp /bin/bash -c “cp -rp /var/lib/mysql/* /tmp/mysql”
```

Now that little thing out of our way it’s time to actually launch your first useful Docker container! Run following command on a separate terminal.

```
chanux@nim:~/docker-lamp$ sudo docker run -i -t -v $(pwd)/mysql:/var/lib/mysql -v $(pwd)/www:/var/www -p 8080:80 mylamp /bin/bash
```

To find out what all these options mean you can just run ‘sudo docker run’ t. In short -i and -t options are there because we want to get a terminal prompt to work with our container. With -v we can bind mount host machines directories on the container. Remember we created mysql and www directories before? Here we mount those on container so mysql data will be persisted between Docker runs (We did that dirty task earlier to make that possible :) ) and we can do changes inside our www directory. Pretty handy.

-p options lets us map a port from host machine to the container. In our case when you go to port 8080 on localhost you’ll be pointed to port 80 on the container.

If everything went all right docker should start and put you on a command prompt. You can start apache by issuing following command

```
root@399d1092ddf6:/# service apache2 start
```

Remember we made our docker command so that it’ll mount the www directory we created on to apache docroot /var/www ? So if we put a simple html file there we could test our web server right? So go ahead and create a file called index.html inside your www directory and unleash your creativity. Just kidding… make it quick!.
Done with the html file? Now is a good time to launch your browser and see how localhost:8080 looks like.

HTML files are fun but we need to see how M and P of LAMP works in Docker. To put php and mysql in the picture, let’s bring in… drumroll… wordpress. Don’t look at me like that. We agreed to KISS, remember?

So the plan is to put wordpress in our www directory, edit the config file and install it. Shall we get on command line and quickly get it done?

```
chanux@nim:~/docker-lamp$ cd www
chanux@nim:~/docker-lamp/www$ wget https://wordpress.org/latest.tar.gz
chanux@nim:~/docker-lamp/www$ tar xzf latest.tar.gz
```

That will extract the sneakily named wordpress tarball, latest.tar.gz in to a directory called wordpress. Go inside wordpress directory and copy wordpress-config-sample.php file to wordpress-config.php. Now open it in an editor and set DB name to ‘wordpress’, DB user to ‘root’ and leave DB password empty like ‘’.

Now get back on the prompt of our docker container. It’s time for some magic. Just say abracadabra!

```
root@399d1092ddf6:/# abracadabra
```

That will start apache and mysql for us. We need to create a database called ‘wordpress’ on mysql. For that run

```
root@399d1092ddf6:/# mysqladmin -uroot create wordpress
```

Now move back to your browser and head to localhost:8080

You should be greeted with Wordpress installation page. I think you can manage this without my help :).

That was just a simple Docker adventure I could imagine. Hope it has provided you with the basics to go on your own adventures. As I’ve mentioned at the start there is another way of building docker images. There you basically run a basic image and install things and do necessary changes in the container by yourself. Once you are done you save the resulting image. You should try that too, there are plenty of tutorials out there.

Also there are docker images from a lot of awesome people on docker index (where you downloaded the basic images from, in our adventure). You want postgresql instead of mysql? There’s an image for that! Or you may want to try out mongodb. Don’t worry the index has it. Believe me or not, one smart guy made a full graphical desktop available on Docker! Even sky is not a limit.

Go on adventures and share with the world. If you ever need help [#docker channel on freenode](webchat.freenode.net/?channels=#docker&nick=) is a good place to be on. [Stackoverflow](http://stackoverflow.com/questions/tagged/docker) is a good place to ask too. Any questions about this guide? email me on chanux at thinkcube dot com.

Huge props to David Cottlehuber for all the great feedback. Also thanks to Kavimal Wijewardena, my colleague and keeb on #docker on freenode.
