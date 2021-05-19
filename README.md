# Guide for the installation of TradEval

We use a Docker container to run TradEval on Windows, Mac OS and Ubuntu.<br>
We will use a Windows X Server which will depend on the OS.<br>

## 1. Docker installation and configuration



## 2. Installation and running of the Windows X Server

### Windows

On Windows, we use the server vcxsrv by running XLaunch.<br>
- Download the executable of vcxsrv at https://sourceforge.net/projects/vcxsrv/ <br>
- Accept the default configuration and install<br>
- Then run XLaunch from the start menu.<br>
- Choose the option "Multiple Windows" and click on Next<br>
- Choose the option "Start no client" and click on Next<br>
- Don't change any parameter and click on Next<br>
- (Optionnal: save the configuration for later running)<br>
- Click on Finish<br>

### Mac OS

On Mac OS, we use the server XQuartz:<br>
- Download the Disk Image file at https://www.xquartz.org/
- Run the installer by double-clicking on the file you dowloaded
- Accept the licence agreement, click on Install
- Once the installation is done, log out from your session and log back in

### Ubuntu

On Ubuntu, we use xauth:<br>
- Install xauth: `sudo apt-get install xauth`


## 3. Running TradEval with Docker


### Ubuntu

Once the X Server is installed and configured, you need to enter the following commands in a terminal.<br>

First, pull the image of the project:<br>
`sudo docker pull pritie/tradeval2`<br>
Then enter:<br>
`xauth list`
The output correspond to a cookie for the session on which the X server is currently running.<br>
Copy the output, you will need it later<br>

Now run the container :<br>
`sudo docker run -ti --net=host -e DISPLAY -v /home:/path_host pritie/tradeval2 bash`<br>
You now have to connect to xauth by entering:
`xauth add COOKIE`<br>
with COOKIE the output of the previous command "xauth list" entered on the host.<br>

You can know execute the python script: `python3 /home/TradEval/tradEval.py`<br>


### Windows / Mac OS

Be sure the X Server is launched (run Xlaunch on Windows, XQuartz on Mac).<br>
Open a terminal.<br>
First, pull the image of the project:<br>
`sudo docker pull pritie/tradeval2`<br>
Then enter:
`docker run -ti --rm -e DISPLAY=IP_ADDRESS:0.0 -v /:/path_host tradeval2`<br>
with IP_ADRESS corresponding to your IP adress. You can find it by typing the command `ipconfig` (windows/mac os) or `ifconfig` (ubuntu) on a terminal.<br>

You can know execute the python script: `python3 /home/TradEval/tradEval.py`<br><br><br>

Note that when you choose a file in tradEval, you can find a file of your host machine in the repository **/path_host**<br>
This repository will give you access to the home repository of your host machine.
