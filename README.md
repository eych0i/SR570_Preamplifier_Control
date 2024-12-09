# SR570_Preamplifier_Control
SR570_Preamplifier_Control is to control settings in **SR570 preamplifer (StandfordResearchSystems)** remotely. 
It can be used for use such as operation inside beamline hutch that is difficult to control directly during measurements.

# Requirements
Before running SR570_Preamplifier_Control, a few preliminary setups are required.

1. Connect SR570 preamplifier software over the RS320-USB cable.
(see https://www.thinksrs.com/products/sr570.html)

3. Install python package as follows: 
pyVisa : https://pyvisa.readthedocs.io/en/latest/
tkinter : https://docs.python.org/3/library/tkinter.html

# Usage
Simply, you can run SR570_Preamplifier_Control.

```
cd sr570_preamplifier_gui
python sr570_preamplifier_gui.py
```



