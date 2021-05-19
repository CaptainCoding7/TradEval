# Guide for the installation of TradEval

We use a Docker container to run TradEval on Windows, Mac OS and Ubuntu.<br>
For Windows and Mac, we will use a Windows X Server.<br>

## 1. Docker installation and configuration



## 2. MAC OS / WINDOWS: Installation and running of the Windows X Server

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

On Mac OS, we use the server XQuartz<br>
- Download the Disk Image file at https://www.xquartz.org/
- Run the installer by double-clicking on the file you dowloaded
- Accept the licence agreement, click on Install
- Once the installation is done, log out from your session and log back in


## 3. Running TradEval with Docker

Once the X Server is installed and configured, all you need to do is entering the following command in a terminal:<br>

`docker run -ti --rm -e DISPLAY=YOUR_IP_ADRESS tradEval`

with YOUR_IP_ADRESS corresponding to your IP adress. You can find it by typing the command `ipconfig` (windows/mac os) or `ifconfig` (ubuntu) on a terminal.
