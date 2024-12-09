import tkinter as tk
from tkinter import ttk
import pyvisa as visa

# the sensitivity of the amplifier
SENSITIVITY_MAP = {
    0: "1 pA/V", 1: "2 pA/V", 2: "5 pA/V", 3: "10 pA/V",
    4: "20 pA/V", 5: "50 pA/V", 6: "100 pA/V", 7: "200 pA/V",
    8: "500 pA/V", 9: "1 nA/V", 10: "2 nA/V", 11: "5 nA/V",
    12: "10 nA/V", 13: "20 nA/V", 14: "50 nA/V", 15: "100 nA/V",
    16: "200 nA/V", 17: "500 nA/V", 18: "1 µA/V", 19: "2 µA/V",
    20: "5 µA/V", 21: "10 µA/V", 22: "20 µA/V", 23: "50 µA/V",
    24: "100 µA/V", 25: "200 µA/V", 26: "1 mA/V"
}

# Input current offset scale
IOLV_MAP = {
    0: "0.1 pA", 1: "0.2 pA", 2: "0.5 pA", 3: "1 pA",
    4: "2 pA", 5: "5 pA", 6: "10 pA", 7: "20 pA",
    8: "50 pA", 9: "0.1 nA", 10: "0.2 nA", 11: "0.5 nA",
    12: "1 nA", 13: "2 nA", 14: "5 nA", 15: "10 nA",
    16: "20 nA", 17: "50 nA", 18: "0.1 µA", 19: "0.2 µA",
    20: "0.5 µA", 21: "1 µA", 22: "2 µA", 23: "5 µA",
    24: "10 µA", 25: "20 µA", 26: "50 µA", 27: "0.1 mA",
    28: "0.2 mA", 29: "0.5 mA"
}

# Filter type 
FILTER_TYPE ={
    0: "6 dB highpass", 1: "12 dB highpass", 2: "6 dB bandpass",
    3: "6 dB lowpass", 4: "12 dB lowpass", 5: "None"
}

# Filter frequency list
LFRQ_LIST = {  # n ranges from 0 (0.03Hz) to 15 (1 MHz) for LFRQ
    0: "0.03 Hz", 1: "0.1 Hz", 2: "0.3 Hz", 3: "1 Hz",
    4: "3 Hz", 5: "10 Hz", 6: "30 Hz", 7: "100 Hz",
    8: "300 Hz", 9: "1 kHz", 10: "3 kHz", 11: "10 kHz",
    12: "30 kHz", 13: "100 kHz", 14: "300 kHz", 15: "1 MHz"
}

HFRQ_LIST = {  # n ranges from 0 (0.03Hz) to 11 (10 kHz) for HFRQ
    0: "0.03 Hz", 1: "0.1 Hz", 2: "0.3 Hz", 3: "1 Hz",
    4: "3 Hz", 5: "10 Hz", 6: "30 Hz", 7: "100 Hz",
    8: "300 Hz", 9: "1 kHz", 10: "3 kHz", 11: "10 kHz",
}

# Gain mode
GAIN_MODE_MAP = {
    0: "Low Noise", 1: "High Bandwidth", 2: "Low Drift"
}

# Bias voltage ON/OFF
BIAS_ON_OFF = {
    0: "OFF", 1: "ON"
}

# invert signal
INVERT_SIGNAL = {
    0: "Non-Inverted", 1: "Inverted"
}

# Blanks 
BLANK_SIGNAL = {
    0: "No Blank", 1: "Blank"
}

class SR570GUI:
    def __init__(self,root):
        self.root = root
        self.root.title("SR570 Pre-amplifier Controller")

        # Initialize Resource Manager for PyVISA
        try:
            self.rm = visa.ResourceManager()
            self.instrument = None
        except Exception as e:
            self.status_label = ttk.Label(root, text=f"Error initializing VISA: {e}", foreground="red")
            self.status_label.grid(row=0, column=0, columnspan=2)
            return

        # Create a Frame for Connection Buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

        # Configure the grid inside the Frame
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Connect Button
        self.connect_button = ttk.Button(button_frame, text="Connect", command=self.connect_device)
        self.connect_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        # Disconnect Button
        self.disconnect_button = ttk.Button(button_frame, text="Disconnect", command=self.disconnect_device)
        self.disconnect_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.disconnect_button["state"] = "disabled"  # Initially disabled

        # Status Label
        self.status_label = ttk.Label(root, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Initialize GUI components
        self.sensitivity_label = None
        self.iolv_label = None
        self.bias_value_label = None
        self.filter_value_label = None
        self.gain_value_label = None
        self.invt_label = None
        self.blnk_label = None

        # Initialize default values
        self.default_values = {
            "sensitivity": 0,  # n=0
            "input_offset_level": 0,  # n=0
            "input_offset_sign": 0,  # Negative (0)
            "bias_state": 0,  # OFF
            "bias_voltage": 0.0,  # 0.0 V
            "filter_type": 5,  # None
            "low_filter_freq": 0,  # 0.03 Hz
            "high_filter_freq": 0,  # 0.03 Hz
            "gain_mode": 0,  # Low Noise
            "invert_signal": 0,  # Non-Inverted
            "blank_output": 0,  # No Blank
        }

        # Create GUI components
        self.add_sensitivity_control(root) # Sensitivity Control
        self.add_input_offset_control(root) # Input Offset Current (IOLV) Control
        self.add_input_offset_sign_control(root) # Input Offset Sign (IOSN) Control
        self.add_bias_voltage_control(root) # Bias voltage Control
        self.add_filter_control(root) # Filter Control
        self.add_gain_mode_control(root) # Gain Mode Control
        self.add_invert_control(root) # Invert Signal Control
        self.add_blank_control(root) # Blank Output Control
        self.add_reset_control(root) # Reset Control

        # Initialize GUI with default values
        self.update_gui_with_defaults()


    def connect_device(self):
        """Connect to the SR570 pre-amplifier using PyVISA."""
        try:
            self.status_label.config(text="Status: Connecting...", foreground="orange")

            # List available VISA resources
            resources = self.rm.list_resources()
            if not resources:
                raise ValueError("No devices found")

            self.instrument = self.rm.open_resource(resources[0])
            self.instrument.write("*RST")  # Reset amplifier 
            self.status_label.config(text="Status: Connected", foreground="green")

            # Apply default values to the instrument
            self.apply_defaults_to_instrument()

            self.connect_button["state"] = "disabled"
            self.disconnect_button["state"] = "normal"

            # Check if components are initialized before accessing them
            if hasattr(self, "sensitivity_label") and self.sensitivity_label:
                self.get_current_sensitivity()
            if hasattr(self, "iolv_label") and self.iolv_label:
                self.get_current_iolv()
            if hasattr(self, "bias_value_label") and self.bias_value_label:
                self.get_current_bias()
            if hasattr(self, "filter_value_label") and self.filter_value_label:
                self.get_current_filter()
            if hasattr(self, "gain_value_label") and self.gain_value_label:
                self.get_current_gain()
            if hasattr(self, "invt_label") and self.invt_label:
                self.get_current_invert()
            if hasattr(self, "blnk_label") and self.blnk_label:
                self.get_current_blank()
            
        except Exception as e:
            self.status_label.config(text=f"Status: Connection Failed ({e})", foreground="red")
            print(f"Connection failed: {e}")  # Debugging output
            self.instrument = None    


    def disconnect_device(self):
        """ disconnect to the SR570 pre-amplifier using pyVISA """
        if self.instrument:
            self.instrument.close()
            self.instrument = None
        self.status_label.config(text='Status: Disconnected', foreground='red')
        self.connect_button['state']= 'normal'
        self.disconnect_button['state'] = 'disabled'

    def update_gui_with_defaults(self):
        """Update GUI with default values safely."""
        if hasattr(self, 'sensitivity_combobox'):
            self.sensitivity_combobox.set(self.default_values["sensitivity"])
        if hasattr(self, 'iolv_combobox'):
            self.iolv_combobox.set(self.default_values["input_offset_level"])
        if hasattr(self, 'iosn_combobox'):
            self.iosn_combobox.set("Negative (0)" if self.default_values["input_offset_sign"] == 0 else "Positive (1)")
        if hasattr(self, 'bson_combobox'):
            self.bson_combobox.set("OFF (0)" if self.default_values["bias_state"] == 0 else "ON (1)")
        if hasattr(self, 'bslv_entry'):
            self.bslv_entry.delete(0, tk.END)
            self.bslv_entry.insert(0, self.default_values["bias_voltage"])
        if hasattr(self, 'filtt_combobox'):
            self.filtt_combobox.set("None (5)")
        if hasattr(self, 'lfrq_combobox'):
            self.lfrq_combobox.set("0.03 Hz (0)")
        if hasattr(self, 'hfrq_combobox'):
            self.hfrq_combobox.set("0.03 Hz (0)")
        if hasattr(self, 'gmd_combobox'):
            self.gmd_combobox.set("Low Noise (0)")
        if hasattr(self, 'invt_combobox'):
            self.invt_combobox.set("Non-Inverted (0)")
        if hasattr(self, 'blnk_combobox'):
            self.blnk_combobox.set("No Blank (0)")

    def apply_defaults_to_instrument(self):
        """Apply default values to the instrument via VISA commands."""
        if not self.instrument:
            return
        try:
            self.instrument.write(f"SENS {self.default_values['sensitivity']}")
            self.instrument.write(f"IOLV {self.default_values['input_offset_level']}")
            self.instrument.write(f"IOSN {self.default_values['input_offset_sign']}")
            self.instrument.write(f"BSON {self.default_values['bias_state']}")
            self.instrument.write(f"BSLV {self.default_values['bias_voltage']}")
            self.instrument.write(f"FLTT {self.default_values['filter_type']}")
            self.instrument.write(f"LFRQ {self.default_values['low_filter_freq']}")
            self.instrument.write(f"HFRQ {self.default_values['high_filter_freq']}")
            self.instrument.write(f"GNMD {self.default_values['gain_mode']}")
            self.instrument.write(f"INVT {self.default_values['invert_signal']}")
            self.instrument.write(f"BLNK {self.default_values['blank_output']}")
        except Exception as e:
            print(f"Error applying defaults to instrument: {e}")


    def add_sensitivity_control(self,root):
        """ Add sensitivty control section """
        ttk.Label(root, text='Sensitivity').grid(row=2, column=0, padx=10, pady=5)
        self.sensitivity_combobox = ttk.Combobox(root, values =[f"{v} ({k})" for k, v in SENSITIVITY_MAP.items()]) 
        self.sensitivity_combobox.grid(row=2, column=1, padx=10, pady=5)
        self.sensitivity_combobox.set(0) # default value

        # self.sensitivity_combobox.bind('<<Comboboxselected>>', self.set_sensitivity) -> this command is used for direct change
        apply_button = ttk.Button(root, text='Apply', command=self.apply_sensitivity)
        apply_button.grid(row=2, column=2, padx=10, pady=5)

        self.sensitivity_label = ttk.Label(root, text='Current Sensitivity: Unknown')
        self.sensitivity_label.grid(row=3, column=0, columnspan=3, pady=5)

    def apply_sensitivity(self):
        """ Apply Sensitivity setting """
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        try:
            selected_value = self.sensitivity_combobox.get()
            n_value = int(selected_value.split("(")[-1].strip(")"))  # Extract the 'n' value
            self.instrument.write(f"SENS {n_value}")  
            scale = SENSITIVITY_MAP.get(n_value, "Unknown")
            self.sensitivity_label.config(text=f"Current Sensitivity: {scale} (n={n_value})", foreground="blue")
            self.status_label.config(text=f"Sensitivity Set: {scale}", foreground="blue")

        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def get_current_sensitivity(self):
        """Retrieve and display the current sensitivity setting."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            n_value = self.default_values["sensitivity"]
            scale = SENSITIVITY_MAP.get(n_value, "Unknown")
            self.sensitivity_label.config(text=f"Current Sensitivity: {scale} (n={n_value})")

        except Exception as e:
            self.sensitivity_label.config(text=f"Error: {e}", foreground="red")        
        
    
    def add_input_offset_control(self, root):
        """ Add Input Offset Current control section """
        
        # IOLV n Value
        ttk.Label(root, text="Input Offset Level").grid(row=4, column=0, padx=10, pady=5)
        self.iolv_combobox = ttk.Combobox(root, values =[f"{v} ({k})" for k, v in IOLV_MAP.items()])  # n=0~29 values=list(IOLV_MAP.keys())
        self.iolv_combobox.grid(row=4, column=1, padx=10, pady=5)
        self.iolv_combobox.set(f"{IOLV_MAP.get(self.default_values['input_offset_level'], 'Unknown')} (0)")  # Default value

        # Apply button for Input Offset Level
        apply_button = ttk.Button(root, text="Apply", command=self.apply_input_offset_level)
        apply_button.grid(row=4, column=2, padx=10, pady=5)

        # Current IOLV Value Display
        self.iolv_label = ttk.Label(root, text="Current Offset: Unknown")
        self.iolv_label.grid(row=5, column=0, columnspan=3, pady=5)

    def apply_input_offset_level(self):
        """ Apply Input Offset Current Level (IOLV n) """ 
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        
        try:
            n_value_IOLV = int(self.iolv_combobox.get().split('(')[-1].strip(')'))  # Get selected n value
            self.instrument.write(f"IOLV {n_value_IOLV}")  
            scale = IOLV_MAP.get(n_value_IOLV, "Unknown")
            self.iolv_label.config(text=f"Current Offset: {scale} (n={n_value_IOLV})", foreground="blue")
            self.status_label.config(text=f"IOLV Set: {scale}", foreground="blue")

        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def get_current_iolv(self):
        """Retrieve and display the current Input Offset Level (IOLV) setting."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            n_value = self.default_values["input_offset_level"]
            scale = IOLV_MAP.get(n_value, "Unknown")
            self.iolv_label.config(text=f"Current Offset: {scale} (n={n_value})")
        except Exception as e:
            self.iolv_label.config(text=f"Error: {e}", foreground="red")

    def add_input_offset_sign_control(self, root):
        """ Add Input Offset Sign (IOSN) control section """
        ttk.Label(root, text='Input Offset Sign').grid(row=6, column=0, padx=10, pady=5)
        self.iosn_combobox = ttk.Combobox(root, values=["Negative (0)", "Positive (1)"])
        self.iosn_combobox.grid(row=6, column=1, padx=10, pady=5)
        self.iosn_combobox.set('Negative (0)')  # Default value

        apply_button = ttk.Button(root, text="Apply", command=self.apply_input_offset_sign)
        apply_button.grid(row=6, column=2, padx=10, pady=5)

        self.iosn_label = ttk.Label(root, text="Current Sign: Unknown")
        self.iosn_label.grid(row=7, column=0, columnspan=3, pady=5)

    def apply_input_offset_sign(self):
        """ Apply Input Offset Sign (IOSN n) """
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        
        try:
            sign_value = 1 if "Positive" in self.iosn_combobox.get() else 0
            self.instrument.write(f"IOSN {sign_value}")  
            self.iosn_label.config(text=f"Current Sign: {'Positive' if sign_value == 1 else 'Negative'}", foreground="blue")
        except Exception as e:
            self.iosn_label.config(text=f"Error: {e}", foreground="red")        

    
    def add_bias_voltage_control(self, root):
        """ Add bias voltage control section """
        ttk.Label(root, text='Bias Voltage On/Off').grid(row=8, column=0, padx=10, pady=5)
        self.bson_combobox = ttk.Combobox(root, values=[f"{v} ({k})" for k, v in BIAS_ON_OFF.items()])
        self.bson_combobox.grid(row=8, column=1, padx=10, pady=5)
        self.bson_combobox.set("OFF (0)")

        bson_apply_button = ttk.Button(root, text="Apply", command=self.apply_bson)
        bson_apply_button.grid(row=8, column=2, padx=10, pady=5)

        ttk.Label(root, text="Bias Voltage (V)").grid(row=9, column=0, padx=10, pady=5)
        self.bslv_entry = ttk.Entry(root)
        self.bslv_entry.grid(row=9, column=1, padx=10, pady=5)

        bslv_apply_button = ttk.Button(root, text="Apply", command=self.apply_bslv)
        bslv_apply_button.grid(row=9, column=2, padx=10, pady=5)

        self.bias_value_label = ttk.Label(root, text="Current Bias Voltage: Unknown")
        self.bias_value_label.grid(row=10, column=0, columnspan=3, pady=5)

    def get_current_bias(self):
        """Retrieve and display the current Bias State and Voltage."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            # Retrieve the current bias state and voltage from the default values or instrument
            n_value = self.default_values.get("bias_state", 0)  # 0: OFF, 1: ON
            bias_state = BIAS_ON_OFF.get(n_value, "Unknown")

            bias_voltage_mv = self.default_values.get("bias_voltage", 0)  # Default in mV
            bias_voltage_v = bias_voltage_mv / 1000  # Convert to volts for display

            # Update the GUI components with the current state and voltage
            self.bson_combobox.set(f"{bias_state} ({n_value})")
            self.bias_value_label.config(
                text=f"State: {bias_state}, Value: {bias_voltage_v:.2f} V")  

        except Exception as e:
            self.bias_value_label.config(text=f"Error: {e}", foreground="red")

    def apply_bson(self):
        """ Apply Bias Voltage On/Off (BSON n)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        
        try:
            selected_value = self.bson_combobox.get()
            n_value = int(selected_value.split("(")[-1].strip(")"))  # Extract numeric value
            self.instrument.write(f"BSON {n_value}")  
            self.default_values["bias_state"] = n_value  # Update default value
            self.bias_value_label.config(text=f"Current Bias set: {BIAS_ON_OFF[n_value]}", foreground="blue")
            self.status_label.config(text=f"Bias Voltage State Set to {BIAS_ON_OFF[n_value]}", foreground="blue")
            self.get_current_bias()  # Update the label to reflect the applied value
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")


    def apply_bslv(self):
        """Apply Bias Voltage Level (BSLV n)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        
        try:
            # bring values from GUI
            user_input = float(self.bslv_entry.get())  # Unit : V
            # Check ranges (-5.0V ~ 5.0V)
            if -5.0 <= user_input <= 5.0:
                # convert V to mV 
                value_mV = int(user_input * 1000)
                # transfter converted voltage values
                self.instrument.write(f"BSON1;BSLV{value_mV}")
                # update voltage input status
                self.default_values["bias_voltage"] = value_mV
                self.status_label.config(text=f"Bias Voltage Set to {user_input:.3f} V", foreground="blue")
            else:
                self.status_label.config(text="Error: Voltage out of range (-5.0V to 5.0V).", foreground="red")
        except ValueError:
            self.status_label.config(text="Error: Invalid input. Please enter a number.", foreground="red")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")
    

    def add_filter_control(self, root):
        """Add Filter Control Section."""
        ttk.Label(root, text="Filter Type").grid(row=11, column=0, padx=10, pady=5)
        self.filtt_combobox = ttk.Combobox(root, values =[f"{v} ({k})" for k, v in FILTER_TYPE.items()]) 
        self.filtt_combobox.grid(row=11, column=1, padx=10, pady=5)
        self.filtt_combobox.set("None (5)")  # Default value

        fltt_apply_button = ttk.Button(root, text="Apply", command=self.apply_fltt)
        fltt_apply_button.grid(row=11, column=2, padx=10, pady=5)


        ttk.Label(root, text="Low Filter Frequency").grid(row=12, column=0, padx=10, pady=5)
        self.lfrq_combobox = ttk.Combobox(root, values=[f"{LFRQ_LIST[k]} ({k})" for k in range(16)])
        self.lfrq_combobox.grid(row=12, column=1, padx=10, pady=5)
        self.lfrq_combobox.set("0.03 Hz (0)")

        lfrq_apply_button = ttk.Button(root, text="Apply", command=self.apply_lfrq)
        lfrq_apply_button.grid(row=12, column=2, padx=10, pady=5)


        ttk.Label(root, text="High Filter Frequency").grid(row=13, column=0, padx=10, pady=5)
        self.hfrq_combobox = ttk.Combobox(root, values=[f"{HFRQ_LIST[k]} ({k})" for k in range(12)])
        self.hfrq_combobox.grid(row=13, column=1, padx=10, pady=5)
        self.hfrq_combobox.set("0.03 Hz (0)")

        hfrq_apply_button = ttk.Button(root, text="Apply", command=self.apply_hfrq)
        hfrq_apply_button.grid(row=13, column=2, padx=10, pady=5)

        reset_button = ttk.Button(root, text="Reset Filter", command=self.reset_filter)
        reset_button.grid(row=14, column=0, columnspan=3, pady=5)

        self.filter_type_label = ttk.Label(root, text="Current Filter Type: Unknown")
        self.filter_type_label.grid(row=15, column=0, padx=10, pady=5)

        self.low_freq_label = ttk.Label(root, text="Low Frequency: Unknown")
        self.low_freq_label.grid(row=15, column=1, padx=10, pady=5)

        self.high_freq_label = ttk.Label(root, text="High Frequency: Unknown")
        self.high_freq_label.grid(row=15, column=2, padx=10, pady=5)


    def apply_fltt(self):
        """Apply Filter Type (FLTT n)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        try:
            value = int(self.filtt_combobox.get().split('(')[-1][0])
            self.instrument.write(f"FLTT {value}")
            self.default_values['filter_type'] = value  # update applied values
            self.get_current_filter()  # update filter status
            self.status_label.config(text=f"Filter Type Set to {self.filtt_combobox.get()}", foreground="blue")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def apply_lfrq(self):
        """Apply Low Filter Frequency (LFRQ n)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        try:
            # Extract selected value from combobox
            value = int(self.lfrq_combobox.get().split('(')[-1].strip(')'))
            
            # Check if value is within valid range for LFRQ
            if 0 <= value <= 15:
                self.instrument.write(f"LFRQ {value}")  
                self.default_values['low_filter_freq'] = value  # Update default value
                self.low_freq_label.config(
                    text=f"Low Frequency: {LFRQ_LIST[value]} (n={value})", 
                    foreground="blue"
                )
                self.status_label.config(
                    text=f"Low Filter Frequency Set to {LFRQ_LIST[value]} (n={value})",
                    foreground="blue"
                )
            else:
                raise ValueError(f"LFRQ value {value} is out of range (0-15).")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def apply_hfrq(self):
        """Apply High Filter Frequency (HFRQ n)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        try:
            # Extract selected value from combobox
            value = int(self.hfrq_combobox.get().split('(')[-1].strip(')'))
            
            # Check if value is within valid range for HFRQ
            if 0 <= value <= 11:
                self.instrument.write(f"HFRQ {value}")  
                self.default_values['high_filter_freq'] = value  # Update default value
                self.high_freq_label.config(
                    text=f"High Frequency: {HFRQ_LIST[value]} (n={value})", 
                    foreground="blue"
                )
                self.status_label.config(
                    text=f"High Filter Frequency Set to {HFRQ_LIST[value]} (n={value})",
                    foreground="blue"
                )
            else:
                raise ValueError(f"HFRQ value {value} is out of range (0-11).")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def reset_filter(self):
        """Reset Filter (ROAD command)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            # Set filter type to 'None'
            self.instrument.write("FLTT 5")  # Command to disable filter (set to None)
            self.default_values.update({
                "filter_type": 5,  # None
                "low_filter_freq": 0,  # Reset low frequency (not applicable)
                "high_filter_freq": 0  # Reset high frequency (not applicable)
            })

            # Update filter type label
            if hasattr(self, 'filter_type_label'):
                self.filter_type_label.config(text="Filter Type: None", foreground="blue")
                # print("Filter Type label updated.")
            else:
                print("Error: 'filter_type_label' is not initialized.")

            # Update low and high frequency labels (not applicable in this mode)
            if hasattr(self, 'low_freq_label'):
                self.low_freq_label.config(text="Low Filter Freq: Not Applicable", foreground="blue")
                # print("Low Filter Frequency label updated.")
            else:
                print("Error: 'low_freq_label' is not initialized.")

            if hasattr(self, 'high_freq_label'):
                self.high_freq_label.config(text="High Filter Freq: Not Applicable", foreground="blue")
                # print("High Filter Frequency label updated.")
            else:
                print("Error: 'high_freq_label' is not initialized.")

            # Display success message
            self.status_label.config(text="Filter Reset to 'None' Successfully", foreground="blue")

        except Exception as e:
            # Handle errors and update the status label
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def get_current_filter(self):
        """Retrieve and display the current Filter Settings."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            # Retrieve current filter settings from default values
            filter_type = self.default_values.get('filter_type', 5)
            low_freq = self.default_values.get('low_filter_freq', 0)
            high_freq = self.default_values.get('high_filter_freq', 0)

            # Map the filter type, low frequency, and high frequency to human-readable values
            filter_name = FILTER_TYPE.get(filter_type, "Unknown")
            low_freq_value = LFRQ_LIST.get(low_freq, "Unknown")
            high_freq_value = HFRQ_LIST.get(high_freq, "Unknown")

            # Update the respective labels with retrieved values
            self.filter_type_label.config(text=f"Filter Type: {filter_name}", foreground="blue")
            self.low_freq_label.config(text=f"Low Frequency: {low_freq_value}", foreground="blue")
            self.high_freq_label.config(text=f"High Frequency: {high_freq_value}", foreground="blue")
        except Exception as e:
            self.status_label.config(text=f"Error updating filter information: {e}", foreground="red")


    def add_gain_mode_control(self, root):
        """ Add gain mode control selection """
        ttk.Label(root, text="Gain Mode").grid(row=16, column=0, padx=10, pady=5)
        self.gmd_combobox = ttk.Combobox(root, values=[f"{v} ({k})" for k, v in GAIN_MODE_MAP.items()])
        self.gmd_combobox.grid(row=16, column=1, padx=10, pady=5)
        self.gmd_combobox.set("Low Noise (0)")

        gmd_apply_button = ttk.Button(root, text="Apply", command=self.apply_gmd)
        gmd_apply_button.grid(row=16, column=2, padx=10, pady=5)

        self.gain_value_label = ttk.Label(root, text="Current Gain Mode: Unknown")
        self.gain_value_label.grid(row=17, column=0, columnspan=3, pady=5)

    def apply_gmd(self):
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:     
            selected_value = self.gmd_combobox.get()
            n_value = int(selected_value.split("(")[-1].strip(")"))  # Extract the 'n' value
            self.instrument.write(f"GNMD {n_value}")  
            scale = GAIN_MODE_MAP.get(n_value, "Unknown")
            self.gain_value_label.config(text=f"Current Gain Mode: {scale} (n={n_value})", foreground="blue")
            self.status_label.config(text=f"Gain Mode Set: {scale}", foreground="blue")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")
    

    def get_current_gain(self):
        """Retrieve and display the current Gain Mode."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            n_value = self.default_values["gain_mode"]
            scale = GAIN_MODE_MAP.get(n_value, "Unknown")
            self.gain_value_label.config(text=f"Current gain mode: {scale} (n={n_value})")
            
        except Exception as e:
            self.gain_value_label.config(text=f"Error: {e}", foreground="red")


    def add_invert_control(self, root):
        """Add Invert Signal Control Section."""
        ttk.Label(root, text="Invert Signal").grid(row=18, column=0, padx=10, pady=5)
        self.invt_combobox = ttk.Combobox(root, values=[f"{v} ({k})" for k, v in INVERT_SIGNAL.items()])
        self.invt_combobox.grid(row=18, column=1, padx=10, pady=5)
        self.invt_combobox.set("Non-Inverted (0)")

        invt_apply_button = ttk.Button(root, text="Apply", command=self.apply_invt)
        invt_apply_button.grid(row=18, column=2, padx=10, pady=5)

        self.invt_label = ttk.Label(root, text="Current Invert: Unknown")
        self.invt_label.grid(row=19, column=0, columnspan=3, pady=5)

    def apply_invt(self):
        """Apply Invert Signal (INVT n)."""
        if not self.instrument:
                self.status_label.config(text="Error: Not connected to any device.", foreground="red")
                return
        try:
            selected_value = self.invt_combobox.get()
            n_value = int(selected_value.split("(")[-1].strip(")"))  # Extract numeric value
            self.instrument.write(f"INVT {n_value}")  
            self.default_values["invert_signal"] = n_value  # Update default value
            self.invt_label.config(text=f"Current set: {INVERT_SIGNAL[n_value]}", foreground = "blue")
            self.status_label.config(text=f"Invert Signal Set to {INVERT_SIGNAL[n_value]}", foreground="blue")
            self.get_current_invert()  # Update the label to reflect the applied value
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")


    def get_current_invert(self):
        """Retrieve and display the current Invert Signal state."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return

        try:
            n_value = self.default_values.get("invert_signal", 0)  # Get the current value from defaults
            invert_text = INVERT_SIGNAL.get(n_value, "Unknown")  # Map to descriptive text
            self.invt_label.config(text=f"Current Invert: {invert_text} (n={n_value})")  # Update label
        except Exception as e:
            self.invt_label.config(text=f"Error: {e}", foreground="red")



    def add_blank_control(self, root):
        """Add Blank Front-End Output Control Section."""
        ttk.Label(root, text="Blank Output").grid(row=20, column=0, padx=10, pady=5)
        self.blnk_combobox = ttk.Combobox(root, values=[f"{v} ({k})" for k, v in BLANK_SIGNAL.items()])
        self.blnk_combobox.grid(row=20, column=1, padx=10, pady=5)
        self.blnk_combobox.set("No Blank (0)")

        blnk_apply_button = ttk.Button(root, text="Apply", command=self.apply_blnk)
        blnk_apply_button.grid(row=20, column=2, padx=10, pady=5)

        self.blnk_label = ttk.Label(root, text="Current Blank State: Unknown")
        self.blnk_label.grid(row=21, column=0, columnspan=3, pady=5)
    
    def apply_blnk(self):
        """Apply Blank Front-End Output (BLNK n)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        try:
            selected_value = self.blnk_combobox.get()
            n_value = int(selected_value.split("(")[-1].strip(")"))  # Extract numeric value
            self.instrument.write(f"BLNK {n_value}")  # Send command to device
            self.default_values["blank_output"] = n_value  # Update default value
            self.blnk_label.config(text=f"Current set: {BLANK_SIGNAL[n_value]})", foreground="blue")
            self.status_label.config(text=f"Blank Output Set to {BLANK_SIGNAL[n_value]}", foreground="blue")
            self.get_current_blank()  # Update the label to reflect the applied value
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red") 

    def get_current_blank(self):
        """Retrieve and display the current Blank Output state."""
        try:
            n_value = self.default_values.get("blank_output", 0)  # Get the current value from defaults
            blank_text = BLANK_SIGNAL.get(n_value, "Unknown")  # Map to descriptive text
            self.blnk_label.config(text=f"Current Blank State: {blank_text} (n={n_value})")  # Update label
        except Exception as e:
            self.blnk_label.config(text=f"Error: {e}", foreground="red")


    def add_reset_control(self, root):
        """Add Reset Amplifier Control Section."""
        reset_button = ttk.Button(root, text="Reset Amplifier", command=self.apply_reset)
        reset_button.grid(row=22, column=0, columnspan=3, pady=10)

    def apply_reset(self):
        """Reset Amplifier to Default Settings (*RST)."""
        if not self.instrument:
            self.status_label.config(text="Error: Not connected to any device.", foreground="red")
            return
        try:
            self.instrument.write("*RST")
            self.status_label.config(text="Amplifier Reset to Default Settings", foreground="blue")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")


if __name__ == '__main__':
    root = tk.Tk()
    app = SR570GUI(root)
    root.mainloop()