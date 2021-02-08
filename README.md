
# SDS 1104X-E Graphical User Interface
This is a simple GUI that I use for remote interfacing with my Siglent SDS 1104X-E Oscilloscope through USB. It is written entirely in Python using the tkinter library.

The GUI includes functionality for setting volts per division and time per division, as well as buttons for saving data and creating quick plots from acquired data. There are also six functional buttons that allow for added custom functionality (I have already added a function for F1).

You will have to update the SIGLENT_SCOPE_ID in the utils file to match the USB address of your own machine (which can be found via the pyvisa resource manager)

The GUI lets you know when the scope is disconnected:
![no_scope](https://github.com/sam-olson/sds1104xe-gui/blob/master/figs/no_scope.png)


And when you're connected:
![yes_scope](https://github.com/sam-olson/sds1104xe-gui/blob/master/figs/yes_scope.png)


An example of the plotting with FFT of a standard sinusoidal wave:
![wave](https://github.com/sam-olson/sds1104xe-gui/blob/master/figs/example_plot.png)
