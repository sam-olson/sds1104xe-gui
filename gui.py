import tkinter as tk
from tkinter import ttk, filedialog
import time
import os

import pyvisa as visa

import utils


class App(tk.Frame):
    '''
    Main GUI app class, inherits from default tkinter Frame class
    '''

    def __init__(self, master=None):
        super().__init__(master)

        # attempt to make a connection to the scope
        self.scope = utils.get_instr(utils.SIGLENT_SCOPE_ID)

        self.master = master
        self.style = ttk.Style()
        self.last_trace = None
        self.folder_loc = os.getcwd() + "/data"

        # configuring placement of trace settings interface
        self.ts_start_col = 4
        self.ts_start_row = 0

        self.grid(column=0, row=0)

        # build subframes
        self.build_frames()
        self.acq_plot(self.acq_plot_frame)
        self.trace_settings(self.trace_frame)
        self.file_io(self.file_frame)
        self.func_butts(self.func_butt_frame)

    def build_frames(self):
        '''
        Method for building all subframes and placing them on the grid
        '''

        # acquisition/plotting subframe
        self.acq_plot_frame = tk.LabelFrame(self)
        self.acq_plot_frame.grid(
            column=0, row=0, columnspan=3, rowspan=5, sticky="ns")

        # trace settings subframe
        self.trace_frame = tk.LabelFrame(self)
        self.trace_frame.grid(column=self.ts_start_col,
                              row=self.ts_start_row, columnspan=3, rowspan=5)

        # file i/o settings subframe
        self.file_frame = tk.LabelFrame(self)
        self.file_frame.grid(column=0, row=6, columnspan=6, rowspan=3)

        # functional buttons subframe
        self.func_butt_frame = tk.LabelFrame(self)
        self.func_butt_frame.grid(column=0, row=9, columnspan=6)

    def trace_settings(self, frame):
        '''
        Method for placing elements in the trace settings subframe. Allows for remote setting of
         volts per division and time per division values

        Parameters
        ----------
        frame: trace_frame subframe created by build_frames
        '''

        # labels for basic information
        self.trace_setting_frame_label = tk.Label(frame,
                                                  text="Channel Settings",
                                                  font="Helvetica 14 bold")
        self.current_label = tk.Label(
            frame, text="Current", font="Helvetica 12 bold")
        self.set_label = tk.Label(frame, text="Set", font="Helvetica 12 bold")

        self.vdiv_label = tk.Label(
            frame, text="V/DIV", font="Helvetica 12 bold")
        self.tdiv_label = tk.Label(
            frame, text="T/DIV", font="Helvetica 12 bold")

        self.vdiv_curr_value = tk.StringVar(frame)
        self.tdiv_curr_value = tk.StringVar(frame)

        # if the scope is connected, grab the current settings
        if self.scope:
            self.vdiv_curr_value = utils.get_vdiv(self.scope)
            self.tdiv_curr_value = utils.get_tdiv(self.scope)

        else:
            self.vdiv_curr_value = "-"
            self.tdiv_curr_value = "-"

        self.vdiv_curr_label = tk.Label(frame, text=f"{self.vdiv_curr_value} V", foreground="blue")
        self.tdiv_curr_label = tk.Label(frame, text=f"{self.tdiv_curr_value} s", foreground="blue")

        self.vdiv_set_value = tk.StringVar(frame)

        # create drop-down menus with options from VDIV_LEVELS and TDIV_LEVELS constants from utils file
        self.vdiv_set = tk.OptionMenu(
            frame, self.vdiv_set_value, *utils.VDIV_LEVELS)
        self.vdiv_set.config(width=10)
        self.tdiv_set_value = tk.StringVar(frame)
        self.tdiv_set = tk.OptionMenu(
            frame, self.tdiv_set_value, *utils.TDIV_LEVELS)
        self.tdiv_set.config(width=10)

        # button for updating values (sends command to scope)
        self.update_button = tk.Button(
            frame, text="Update", command=self.update_scale)

        # setting layout for trace setting widgets on grid
        self.trace_setting_frame_label.grid(column=self.ts_start_col,
                                            row=self.ts_start_row,
                                            columnspan=3,
                                            sticky="ew")
        self.current_label.grid(column=self.ts_start_col + 1,
                                row=self.ts_start_row + 1)
        self.set_label.grid(column=self.ts_start_col + 2,
                            row=self.ts_start_row + 1)
        self.vdiv_label.grid(column=self.ts_start_col,
                             row=self.ts_start_row + 2)
        self.tdiv_label.grid(column=self.ts_start_col,
                             row=self.ts_start_row + 3)
        self.vdiv_curr_label.grid(column=self.ts_start_col + 1,
                                  row=self.ts_start_row + 2)
        self.tdiv_curr_label.grid(column=self.ts_start_col + 1,
                                  row=self.ts_start_row + 3)
        self.vdiv_set.grid(column=self.ts_start_col + 2,
                           row=self.ts_start_row + 2)
        self.tdiv_set.grid(column=self.ts_start_col + 2,
                           row=self.ts_start_row + 3)
        self.update_button.grid(column=self.ts_start_col + 2,
                                row=self.ts_start_row + 4)

    def acq_plot(self, frame):
        '''
        Method for placing elements in the plot/acquisition subframe.

        Parameters
        ----------
        frame: acq_plot_frame subframe created by build_frames
        '''

        self.scope_status = tk.StringVar(frame)

        # determine if scope is connected, adjust display accordingly
        if self.scope:
            self.scope_status = "Scope Connected!"
            self.scope_status_color = "green"
        else:
            self.scope_status = "No Scope!"
            self.scope_status_color = "red"

        self.scope_status_label = tk.Label(
            frame, text=self.scope_status, background=self.scope_status_color)
        self.scope_status_label.grid(
            column=0, row=0, columnspan=3, sticky="ew")

        # button for establishing connection with scope
        self.connect_button = tk.Button(
            frame, text="Connect Scope", command=self.connect_scope)
        self.connect_button.grid(column=0, row=1, columnspan=3, sticky="ew")

        # button for plotting a trace
        self.plot_button = tk.Button(
            frame, text="Plot Trace", command=self.plot_file)
        self.plot_button.grid(column=0, row=3, columnspan=3, sticky="ew")

        # button for plotting most recent trace collected
        self.plot_last = tk.Button(
            frame, text="Plot Last", command=self.plot_last_trace)
        self.plot_last.grid(column=0, row=4, columnspan=3, sticky="ew")

        # creating a checkbox to allow user to plot trace w/ FastF ourier Transform (FFT) enabled
        self.fft_check_value = tk.IntVar(frame, value=0)
        self.fft_check = tk.Checkbutton(
            frame, variable=self.fft_check_value, text="w/ FFT?")
        self.fft_check.grid(column=0, row=5, columnspan=3, sticky="ew")

    def file_io(self, frame):
        '''
        Method for placing elements in the file i/o subframe.

        Parameters
        ----------
        frame: file_frame subframe created by build_frames
        '''

        # label to let user know where acquired data will be saved
        self.folder_loc_label = tk.Label(frame,
                                         text=f"Current folder: ...{self.folder_loc[-20:]}")
        self.folder_loc_label.grid(column=0, row=0, columnspan=4, sticky="ew")

        # button to change where acquired data will be saved
        self.change_folder_butt = tk.Button(
            frame, text="Change", command=self.change_folder)
        self.change_folder_butt.grid(
            column=5, row=0, columnspan=2, sticky="ew")

        # allow user to create a custom file name...
        self.fname_label = tk.Label(frame, text="Filename: ")
        self.fname_label.grid(column=0, row=1, sticky="ew")
        self.fname_entry = tk.Entry(frame)
        self.fname_entry.grid(column=1, row=1, columnspan=3, sticky="ew")

        # ...or use the default timestamp
        self.file_check_value = tk.IntVar(frame, value=1)
        self.file_checkbox = tk.Checkbutton(
            frame, variable=self.file_check_value, text="Default\n(timestamp)")
        self.file_checkbox.grid(column=6, row=1, sticky="ew")

        # button to acquire a trace from the scope as it is currently displayed on screen
        self.acquire_button = tk.Button(
            frame, text="Acquire Trace", command=self.acquire_data)
        self.acquire_button.grid(column=0, row=2, columnspan=8, sticky="ew")

    def func_butts(self, frame):
        '''
        Method for placing elements in the functional buttons subframe. These buttons allow the user
            to create their own routines for interacting with the oscilloscope

        Parameters
        ----------
        frame: func_butt_frame subframe created by build_frames
        '''

        self.func_butts_section_label = tk.Label(
            frame, text="Functional Buttons")
        self.func_butts_section_label.grid(
            column=0, row=0, columnspan=6, sticky="ew")

        # allow for customizable functional buttons (currently only F1 is implemented)
        self.func_butt_1 = tk.Button(frame, text="F1", command=self.f1_command)
        self.func_butt_2 = tk.Button(frame, text="F2")
        self.func_butt_3 = tk.Button(frame, text="F3")
        self.func_butt_4 = tk.Button(frame, text="F4")
        self.func_butt_5 = tk.Button(frame, text="F5")
        self.func_butt_6 = tk.Button(frame, text="F6")

        self.func_butt_1.grid(column=0, row=1)
        self.func_butt_2.grid(column=1, row=1)
        self.func_butt_3.grid(column=2, row=1)
        self.func_butt_4.grid(column=0, row=2)
        self.func_butt_5.grid(column=1, row=2)
        self.func_butt_6.grid(column=2, row=2)

    def scope_conn(self):
        '''
        Method for setting the scope status to connected (sets background of label to green)
        '''

        self.scope_status_label["text"] = "Scope Connected!"
        self.scope_status_label["background"] = "green"
        self.vdiv_curr_label["text"] = f"{utils.get_vdiv(self.scope)} V"
        self.tdiv_curr_label["text"] = f"{utils.get_tdiv(self.scope)} s"

    def scope_disconn(self):
        '''
        Method for setting the scope status to disconnected (sets background of label to red)
        '''

        self.scope_status_label["text"] = "No Scope!"
        self.scope_status_label["background"] = "red"
        self.vdiv_curr_label["text"] = "- V"
        self.tdiv_curr_label["text"] = "- s"

    def connect_scope(self):
        '''
        Method for attempting to establish communication with the oscilloscope
        '''

        self.scope = utils.get_instr(utils.SIGLENT_SCOPE_ID)

        if self.scope:
            self.scope_conn()
        else:
            self.scope_disconn()

    def acquire_data(self):
        '''
        Method for acquiring a trace from the oscilloscope
        '''

        self.scope = utils.get_instr(utils.SIGLENT_SCOPE_ID)

        # if the scope is connected...
        if self.scope:
            # if the user wants to use the default timestamp filename
            if self.file_check_value.get():
                self.last_trace = f"{utils.timestamp()}.csv"

            # if they want to use a custom filename, do some validation
            else:
                self.last_trace = self.fname_entry.get()
                if not self.last_trace.endswith(".csv"):
                    self.last_trace += ".csv"
            self.last_trace = f"{self.folder_loc}/{self.last_trace}"
            self.scope_conn()
            utils.acquire(self.last_trace)

        # if the connection could not be established, update the display
        else:
            self.scope_disconn()

    def plot_file(self):
        '''
        Method for plotting a file as selected by the user
        '''

        # open up a filedialog to let the user navigate to the appropriate file
        fpath = filedialog.askopenfilename()

        if fpath:
            # if they want to display with FFT
            if self.fft_check_value.get():
                utils.plot_data_with_fft(fpath)
            else:
                utils.plot_data(fpath)

    def plot_last_trace(self):
        '''
        Method for plotting the most recent trace (if it exists)
        '''

        if self.last_trace:
            try:
                utils.plot_data(self.last_trace)
            except:
                print(f"Cannot find trace {file_to_open}")
        else:
            print("No trace acquired in this session")

    def update_scale(self):
        '''
        Method for updating VDIV/TDIV as set by user in the GUI
        '''

        # make sure the scope is listening
        self.scope = utils.get_instr(utils.SIGLENT_SCOPE_ID)

        if self.scope:
            self.scope_conn()

            # set the values
            v_set = self.vdiv_set_value.get()
            t_set = self.tdiv_set_value.get()

            if v_set:
                utils.set_vdiv(self.scope, v_set)
                self.vdiv_curr_label["text"] = v_set
            if t_set:
                utils.set_tdiv(self.scope, t_set)
                self.tdiv_curr_label["text"] = t_set
        else:
            self.scope_disconn()

    def change_folder(self):
        '''
        Method for allowing user to change the current save directory
        '''

        self.folder_loc = filedialog.askdirectory()
        self.folder_loc_label["text"] = f"Current folder: ...{self.folder_loc[-20:]}"

    def f1_command(self):
        '''
        Method representing the functionality of functional button F1
        '''
        self.scope = utils.get_instr(utils.SIGLENT_SCOPE_ID)

        if self.scope:
            self.scope_conn()
            utils.fit_wave(self.scope)
        else:
            self.scope_disconn()


if __name__ == "__main__":
    # run the GUI!
    root = tk.Tk()
    root.title("Siglent SDS 1104X-E")
    root.resizable(False, False)
    app = App(master=root)
    app.mainloop()
