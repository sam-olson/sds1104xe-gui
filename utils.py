import re
import datetime

import pyvisa as visa
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftfreq
import numpy as np

# address of your scope on your machine (will be different)
SIGLENT_SCOPE_ID = 'USB0::0xF4EC::0xEE38::SDSMMEBQ4R5668::0::INSTR'

# allowable VDIV levels
VDIV_LEVELS = ["500 uV",
               "1 mV",
               "2 mV",
               "5 mV",
               "10 mV",
               "20 mV",
               "50 mV",
               "100 mV",
               "200 mV",
               "500 mV",
               "1 V",
               "2 V",
               "5 V",
               "10 V"
    ]

# allowable TDIV levels
TDIV_LEVELS = ["1 ns",
               "2 ns",
               "5 ns",
               "10 ns",
               "20 ns",
               "50 ns",
               "100 ns",
               "200 ns",
               "500 ns",
               "1 us",
               "2 us",
               "5 us",
               "10 us",
               "20 us",
               "50 us",
               "100 us",
               "200 us",
               "500 us",
               "1 ms",
               "2 ms",
               "5 ms",
               "10 ms",
               "20 ms",
               "50 ms",
               "100 ms",
               "200 ms",
               "500 ms",
               "1 s",
               "2 s",
               "5 s",
               "10 s",
               "20 s",
               "50 s",
               "100 s"
               ]

# TDIV levels as floats for calculations
TDIV_FLOATS = [1.0e-9,
               2.0e-9,
               5.0e-9,
               10.0e-9,
               20.0e-9,
               50.0e-9,
               100.0e-9,
               200.0e-9,
               500.0e-9,
               1.0e-6,
               2.0e-6,
               5.0e-6,
               10.0e-6,
               20.0e-6,
               50.0e-6,
               100.0e-6,
               200.0e-6,
               500.0e-6,
               1.0e-3,
               2.0e-3,
               5.0e-3,
               10.0e-3,
               20.0e-3,
               50.0e-3,
               100.0e-3,
               200.0e-3,
               500.0e-3,
               1.0,
               2.0,
               5.0,
               10.0,
               20.0,
               50.0,
               100.0
               ]
               

def timestamp():
    '''
    Returns the current time as a timestamp
    ex: 20210207_172143 (Feb 7, 2021 at 17:21:43)
    '''
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def match_tdiv(t):
    '''
    Matches a given TDIV value to one of the allowed TDIV levels

    Parameters
    ----------
    t: TDIV value to be matched

    Returns
    --------
    the matched allowable TDIV value
    '''
    
    ret_val = None
    for i in range(len(TDIV_FLOATS)-1):
        if (t > TDIV_FLOATS[i]) and (t < TDIV_FLOATS[i+1]):
            lower = abs(t - TDIV_FLOATS[i])
            upper = abs(t - TDIV_FLOATS[i+1])
            if lower < upper:
                ret_val = TDIV_LEVELS[i]
            else:
                ret_val = TDIV_LEVELS[i+1]
    return ret_val

def get_instr(instr_id):
    '''
    Establishes a connection with the oscilloscope

    Parameters
    ----------
    instr_id: VISA ID for the scope

    Returns
    ---------
    a pyvisa object representing the scope
    '''
    
    rm = visa.ResourceManager()

    # check that there are actually instrument(s) connected
    if len(rm.list_resources()) == 0:
        return None

    # attempt to establish a connection
    try:
        instr = rm.open_resource(instr_id)
        print(f"Found instrument: {instr.manufacturer_name} {instr.model_name}")
        return instr
    except:
        print("No instrument detected!")
        return None

def smart_query(instr, command):
    '''
    Sends a query to the scope that doesn't get hung up

    Parameters
    ----------
    instr: pyvisa instrument object representing the scope
    command: SCPI command to be sent to the scope

    Returns
    ---------
    information from the scope, based on what command was sent
    '''
    
    try:
        return instr.query(command)
    except visa.errors.VisaIOError:
        return None


def calc_voltage(num, v_div, v_offset=0):
    '''
    Converts ADC voltage value from oscilloscope to the actual voltage level

    Parameters
    ----------
    num: ADC voltage from scope
    v_div: current volts per division
    v_offset: voltage offset (optional, defaults to 0 V)
    '''
    
    num = int(num)
    if num > 127:
        num = num - 255
    return num * (v_div / 25) - v_offset


def get_tdiv(scope):
    '''
    Sends query to scope and parses time per division (TDIV) information from return string

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope

    Returns
    --------
    the time per division, or None if the parsing fails (if the string does not contain the TDIV)
    '''
    
    data = smart_query(scope, "TDIV?")
    try:
        return float(re.findall("TDIV\s(.*)S", data)[0])
    except:
        return None


def get_vdiv(scope):
    '''
    Sends query to scope and parses volts per division (VDIV) information from return string
        (Currently only supports Channel 1 queries)

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope

    Returns
    --------
    the volts per division, or None if the parsing fails (if the string does not contain the VDIV)
    '''
    
    data = smart_query(scope, "C1:VDIV?")
    try:
        return float(re.findall("\w\d:VDIV\s(.*)V", data)[0])
    except:
        return None


def get_offset(scope):
    '''
    Sends query to scope and parses voltage offset (OFST) information from return string
        (Currently only supports Channel 1 queries)

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope

    Returns
    --------
    the voltage offset, or None if the parsing fails (if the string does not contain the OFST)
    '''
    
    data = smart_query(scope, "C1:OFST?")
    try:
        return float(re.findall("\w\d:OFST\s(.*)V", data)[0])
    except:
        return None

def get_sara(scope):
    '''
    Sends query to scope and parses the sample rate (SARA) information from return string

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope

    Returns
    --------
    the sample rate, or None if the parsing fails (if the string does not contain the SARA)
    '''
    
    data = smart_query(scope, "SARA?")
    try:
        return float(re.findall("SARA\s(.*)Sa/s", data)[0])
    except:
        return None

def get_freq(scope):
    '''
    Sends query to scope and parses estimated frequency (CYMT) information from return string

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope

    Returns
    --------
    the estimated frequency of the signal, or None if the parsing fails (if the string does not contain the CYMT)
    '''
    
    data = smart_query(scope, "CYMT?")
    try:
        return float(re.findall("CYMT\s(.*)Hz", data)[0])
    except:
        return None

def get_max(scope):
    '''
    Sends query to scope and parses maximum voltage information from return string

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope

    Returns
    --------
    the maximum voltage, or None if the parsing fails
    '''
    data = smart_query(scope, "C1:PAVA? MAX")
    try:
        return float(re.findall("C1:PAVA\sMAX,(.*)V", data)[0])
    except:
        return None

def set_vdiv(scope, level):
    '''
    Sends query to scope and sets volts per division (VDIV)
        (Currently only supports Channel 1 queries)

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope
    level: desired volts per division
    '''
    
    try:
        smart_query(scope, f"C1:VDIV {level}")
    except:
        print("Invalid VDIV level!")

def set_tdiv(scope, level):
    '''
    Sends query to scope and sets time per division (VDIV)

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope
    level: desired time per division
    '''
    
    try:
        smart_query(scope, f"TDIV {level}")
    except:
        print("Invalid TDIV level!")

def fit_wave(scope):
    '''
    Attempts to fit a single period of a sinusoidal wave on the oscilloscope display.
        This function represents the functionality of functional button 1

    Parameters
    ----------
    scope: pyvisa instrument object representing the oscilloscope
    '''
    
    freq = get_freq(scope)
    set_vdiv(scope, 1)
    max_v = get_max(scope)
    if freq:
        wavelength = 1 / freq
        per_div = wavelength / 7
        set_time = match_tdiv(per_div)
        set_tdiv(scope, set_time)
        set_vdiv(scope, max_v)

        # set the trigger level to the max voltage
        smart_query(scope, f"C1:TRLV {max_v}")
        smart_query(scope, "TRMD SINGLE")

def acquire(fpath):
    '''
    Acquires a trace from the oscilloscope. Currently only supports channel 1

    Parameters
    ----------
    fpath: file path to save the resulting trace
    '''
    
    rm = visa.ResourceManager()
    try:
        scope = rm.open_resource(SIGLENT_SCOPE_ID)
    except:
        print("No instrument detected!")
        scope = None
        
    if scope:
        v_div = get_vdiv(scope)
        offset = get_offset(scope)
        sara = get_sara(scope)

        # send a write command to the scope to get the data from channel 1
        scope.write("C1:WF? DAT2")

        # read in the data and ignore the header
        raw_data = scope.read_raw()[22:]

        # chop off the last two values that tell you the trace is over
        raw_data = raw_data[:len(raw_data) - 3]

        processed_data = [calc_voltage(i, v_div, offset) for i in raw_data]
        t = [i / sara for i in range(len(processed_data))]

        # create a pandas data frame to save the data as a .csv
        df = pd.DataFrame(data={"Time (s)":t, "Voltage (V)":processed_data})
        df.to_csv(fpath, index=None)

def fourier(t, v):
    '''
    Crude FFT functionality

    Parameters
    ----------
    t: time data
    v: voltage data

    Returns
    --------
    FFT-ized time and voltage data as a tuple
    '''
    
    sample_rate = t[1] - t[0]

    n = len(t)

    t_f = fftfreq(n, sample_rate)[:n//2]
    v_f = (2.0/n) * np.abs(fft(v)[0:n//2])
    
    
    return (t_f, v_f)
    

def plot_data(fname):
    '''
    Plots data for a given filename, unless the data is too big

    Parameters
    ---------
    fname: file name to plot from
    '''
    
    df = pd.read_csv(fname)
    t = df["Time (s)"]
    v = df["Voltage (V)"]

    try:
        plt.plot(t,v)
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.show()
    except:
        print("Filesize too large!")

def plot_data_with_fft(fname):
    '''
    Displays a double plot, with both standard and FFT-ed data

    Parameters
    ----------
    fname: file name to plot from
    '''
    
    df = pd.read_csv(fname)
    t = df["Time (s)"]
    v = df["Voltage (V)"]
    t_f, v_f = fourier(t, v)

    try:
        plt.subplot(211)
        plt.plot(t,v)
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")

        plt.subplot(212)
        plt.plot(t_f, v_f)
        plt.xlim([0,2000000])
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude (arb.)")
        plt.show()
    except:
        print("Filesize too large!")
    
