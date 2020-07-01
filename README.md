This program is a GUI for capturing PPG data with a max30101 ppg sensor on a raspberry pi. 

To install it


To run it, just run 
`python iclppg
or 
`python3 iclppg


Raspberry pi setup:

With our ppg boards you need to get access to or generate 1.8V. On a Pi4 it is TP13, on other Pi's it will be different.

Connect the PPG sensor I2C pins to the pi GPIOs (sda - 3 & scl - 5). Interrupt pin is currently set to pin 26. Connect power pins as appropriate.

On the PI:

enable i2c:
`sudo raspi-config`
then navigate to interfaces and enable it (may need to restart)

install i2c tools
`sudo apt-get install i2c-tools`

wire the board up and test whether communication is happening:
`i2cdetect -y 1`

get the necessary python packages:

`pip install smbus2 gpiozero argparse python-statemachine typing

get pyqt5
`sudo apt-get update && apt-get install python-pyqt5

We need the dev branch of pyqtgraph otherwise you get an error about time not having a clock function (python 3.8 removed that function). Best way is to
if you have pyqtgraph already - uninstall it   with 
`pip uninstall pyqtgraph`
then get the latest pyqtgraph:
`git clone https://github.com/pyqtgraph/pyqtgraph.git`
in the repo directory run 
`sudo python setup.py install`

Change the i2c speed too
`sudo nano /boot/config.txt
Find the line containing “dtparam=i2c_arm=on”.
Add “,i2c_arm_baudrate=400000” where 400000 is the new speed (400 Kbit/s). Note the comma.
This should give you a line looking like :
`dtparam=i2c_arm=on,i2c_arm_baudrate=400000
`sudo reboot
