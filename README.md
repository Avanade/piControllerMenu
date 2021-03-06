# Overview
This repo contains a Raspberry PI controller menu that allows interaction with the RPi via a mini LCD display and 5 tactile 
buttons connected via GPIO. This is helpful in situations where you want to use your RPi headless, without screen, keybaord and mouse
(such a process control or process automation scenarios) but want to interact and control your PI locally (ssh is not always convenient). 

This is very similar to functionality to your have on PLCs that allow local interaction, program execution and status from a 
built-in mini display. 

To see it in action, click on the image below for a brief YouTube video. 

[![See it in action](controllerMenu.jpg)](https://youtu.be/ZApU0XuNtY8 "See it in action")

# Hardware

1. 1x RPi 3 or 4
2. 1x Waveshare 1.8in 128x160 LCD Display - https://www.amazon.com/gp/product/B0785SRXDG/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1
3. 5x Micro Tactile Buttons - https://www.amazon.com/gp/product/B07HBBGRGM/ref=ppx_yo_dt_b_asin_title_o08_s01?ie=UTF8&psc=1

Buttons share a common connection via a 1K resistor to 3.3V. The other side of the buttons are connected to GPIO pins (BCM Numbering) as follows:

    Up Button       ->  GPIO BCM 17
    Down Button     ->  GPIO BCM 5
    Left Button     ->  GPIO BCM 6
    Right Button    ->  GPIO BCM 22
    Select Button   ->  GPIO BCM 18

Schematic to be published. 

# Software

1. Python 3.7 or higher
2. RPI.GPIO
3. PIL/Pillow
4. py-yaml
5. Spidev

# Basic Functionality
The menu is installed as a service at boot time. It has the ability for user defined root and sub menus as well as process execution 
or arbitary commands (as long as you can run them from a shell). Configurably, commands can reqiure confirmation and report back on execution
status. 

# Built-in commands
There are currently two built-in commands:

1. sysInfo - this command provides a systems overview, including: IP address, average load, memory utilization, disk utilization and temperature
2. network - this command provides information about the RPi's network capability, including available interfaces and MAC addresses. 

# Sample Menu
The project has an included sample menu (controllerMenu.yaml) to illustrate the configuration. The menu has the following structure

    Root                            # Root Menu
      |-- Demo Routines             # Demo sub menu
      |     |-- Robot Arm Test      # Invokes test routine for robot arm
      |     |-- Pump Test           # Invokes test routine for pump
      |-- System Information        # Invokes sysInfo built-in command
      |-- Admin                     # Admin sub menu
            |-- Reboot              # Reboots the RPi
            |-- Shutdown            # Shutsdown the RPi
            |-- Network             # Invokes the network built-in command


# Installation

1. Install dependencies (above)
2. Clone this repo to your RPi
3. Edit controllerMenu.yaml to your specifications
4. Make entry point executable
    ```chmod 755 __main__.py```
5. Create symbolic link to service definition
    ```sudo ln -s <path to controllerMenu.service> /etc/systemd/system/controllerMenu.service```
6. Configure menu for start on boot
    ```sudo systemctl enable controllerMenu.service```
7. Start menu manually
    ```sudo systemctl start controllerMenu.service```

# DIN Rail Case for DIN mounting
To be added once I post the 3D models on Thingiverse


# Related Items

1. meArm REST API - https://app.swaggerhub.com/apis-docs/thor-schueler/Avanade.meArm.API.REST/1.0.0
2. meArm REST API and Azure IoT Hub implementation - https://github.com/Avanade/meArmPi
3. To create a meArm (3D Print) - https://www.thingiverse.com/thing:1550041
