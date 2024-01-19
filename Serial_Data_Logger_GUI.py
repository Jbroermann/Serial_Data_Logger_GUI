import tkinter as tk
from tkinter import ttk, filedialog
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import csv
import sys

class SerialPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Plotter")

        self.port_label = ttk.Label(root, text="Serial Port:")
        self.port_entry = ttk.Entry(root)
        self.port_entry.insert(0, "COM1")  # Change this to your port

        self.start_button = ttk.Button(root, text="Start", command=self.start_reading)
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_reading)
        self.save_button = ttk.Button(root, text="Save Data", command=self.save_to_csv)
        self.close_button = ttk.Button(root, text="Close", command=self.close_program)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.port_label.pack(pady=10)
        self.port_entry.pack(pady=10)
        self.start_button.pack(pady=10)
        self.stop_button.pack(pady=10)
        self.save_button.pack(pady=10)
        self.close_button.pack(pady=10)

        self.serial_port = None
        self.is_reading = False
        self.data = []

    def start_reading(self):
        port = self.port_entry.get()
        try:
            self.serial_port = serial.Serial(port, baudrate=9600, timeout=1)
            self.is_reading = True
            threading.Thread(target=self.read_serial).start()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def read_serial(self):
        x_data = []
        y_data = []

        while self.is_reading:
            try:
                line = self.serial_port.readline().decode().strip()
                value = int(line)

                x_data.append(len(x_data) + 1)
                y_data.append(value)

                # Set x-axis limit to a fixed range (e.g., from 0 to 50)
                self.ax.set_xlim(0, 50)

                # Set y-axis limit dynamically based on the maximum value received
                max_value = max(y_data)
                self.ax.set_ylim(0, max_value + 10)

                self.ax.clear()
                self.ax.plot(x_data, y_data, marker='o')
                self.ax.set_title("Serial Data Plot")
                self.ax.set_xlabel("Data Point")
                self.ax.set_ylabel("Value")

                self.canvas.draw()

                # Append data to the list for saving to CSV
                self.data.append([len(x_data), value])

            except (ValueError, UnicodeDecodeError):
                pass  # Ignore non-integer values

    def stop_reading(self):
        if self.is_reading:
            self.is_reading = False
            if self.serial_port:
                self.serial_port.close()

    def save_to_csv(self):
        if self.data:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                with open(file_path, mode="w", newline="") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(["Data Point", "Value"])
                    csv_writer.writerows(self.data)
                print(f"Data saved to {file_path}")

    def close_program(self):
        self.stop_reading()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    plotter = SerialPlotter(root)
    root.protocol("WM_DELETE_WINDOW", plotter.close_program)  # Handle window close event
    root.mainloop()
