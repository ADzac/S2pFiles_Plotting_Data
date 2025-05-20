import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import re

def parse_s2p_file(file_path):
    """
    Parse an S2P file and extract frequency and S-parameters.
    
    Returns:
    - freq: frequency values
    - s_params: dictionary containing S-parameters (S11, S12, S21, S22) in different formats
    """
    # Read the file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Extract the header line to determine format
    header = None
    data_lines = []
    
    for line in lines:
        # Skip empty lines and comments that don't contain format information
        if not line.strip() or line.strip().startswith('!') and not '# ' in line:
            continue
        
        # Look for format line
        if '# ' in line and header is None:
            header = line.strip()
        # Data lines
        elif not line.strip().startswith('!'):
            data_lines.append(line.strip())
    
    # Determine the format from the header
    format_str = "DB" # Default format
    if header:
        if "DB" in header:
            format_str = "DB"
        elif "MA" in header:
            format_str = "MA"
        elif "RI" in header:
            format_str = "RI"
    
    # Convert data to numpy array
    data = []
    for line in data_lines:
        try:
            values = [float(x) for x in line.split()]
            if len(values) >= 9:  # Expect at least 9 values (freq + 4 complex params)
                data.append(values)
        except ValueError:
            continue
    
    if not data:
        raise ValueError("No valid data found in the file.")
    
    data_array = np.array(data)
    
    # Extract frequency (first column)
    freq = data_array[:, 0]
    
    # Extract S-parameters based on the format
    s_params = {
        'S11': {'mag': [], 'phase': [], 'real': [], 'imag': []},
        'S21': {'mag': [], 'phase': [], 'real': [], 'imag': []},
        'S12': {'mag': [], 'phase': [], 'real': [], 'imag': []},
        'S22': {'mag': [], 'phase': [], 'real': [], 'imag': []}
    }
    
    if format_str == "DB":
        # DB format: magnitude in dB, phase in degrees
        s11_mag_db = data_array[:, 1]
        s11_phase = data_array[:, 2]
        s21_mag_db = data_array[:, 3]
        s21_phase = data_array[:, 4]
        s12_mag_db = data_array[:, 5]
        s12_phase = data_array[:, 6]
        s22_mag_db = data_array[:, 7]
        s22_phase = data_array[:, 8]
        
        # Convert from dB to linear magnitude
        s11_mag = 10**(s11_mag_db/20)
        s21_mag = 10**(s21_mag_db/20)
        s12_mag = 10**(s12_mag_db/20)
        s22_mag = 10**(s22_mag_db/20)
        
        # Store magnitude and phase
        s_params['S11']['mag'] = s11_mag_db  # Store the dB value for plotting
        s_params['S11']['phase'] = s11_phase
        s_params['S21']['mag'] = s21_mag_db
        s_params['S21']['phase'] = s21_phase
        s_params['S12']['mag'] = s12_mag_db
        s_params['S12']['phase'] = s12_phase
        s_params['S22']['mag'] = s22_mag_db
        s_params['S22']['phase'] = s22_phase
        
        # Convert to real and imaginary parts for potential future use
        s_params['S11']['real'] = s11_mag * np.cos(np.radians(s11_phase))
        s_params['S11']['imag'] = s11_mag * np.sin(np.radians(s11_phase))
        s_params['S21']['real'] = s21_mag * np.cos(np.radians(s21_phase))
        s_params['S21']['imag'] = s21_mag * np.sin(np.radians(s21_phase))
        s_params['S12']['real'] = s12_mag * np.cos(np.radians(s12_phase))
        s_params['S12']['imag'] = s12_mag * np.sin(np.radians(s12_phase))
        s_params['S22']['real'] = s22_mag * np.cos(np.radians(s22_phase))
        s_params['S22']['imag'] = s22_mag * np.sin(np.radians(s22_phase))
    
    elif format_str == "MA":
        # MA format: linear magnitude and phase in degrees
        s11_mag = data_array[:, 1]
        s11_phase = data_array[:, 2]
        s21_mag = data_array[:, 3]
        s21_phase = data_array[:, 4]
        s12_mag = data_array[:, 5]
        s12_phase = data_array[:, 6]
        s22_mag = data_array[:, 7]
        s22_phase = data_array[:, 8]
        
        # Convert to dB for plotting
        s_params['S11']['mag'] = 20 * np.log10(s11_mag)
        s_params['S11']['phase'] = s11_phase
        s_params['S21']['mag'] = 20 * np.log10(s21_mag)
        s_params['S21']['phase'] = s21_phase
        s_params['S12']['mag'] = 20 * np.log10(s12_mag)
        s_params['S12']['phase'] = s12_phase
        s_params['S22']['mag'] = 20 * np.log10(s22_mag)
        s_params['S22']['phase'] = s22_phase
        
        # Real and imaginary parts
        s_params['S11']['real'] = s11_mag * np.cos(np.radians(s11_phase))
        s_params['S11']['imag'] = s11_mag * np.sin(np.radians(s11_phase))
        s_params['S21']['real'] = s21_mag * np.cos(np.radians(s21_phase))
        s_params['S21']['imag'] = s21_mag * np.sin(np.radians(s21_phase))
        s_params['S12']['real'] = s12_mag * np.cos(np.radians(s12_phase))
        s_params['S12']['imag'] = s12_mag * np.sin(np.radians(s12_phase))
        s_params['S22']['real'] = s22_mag * np.cos(np.radians(s22_phase))
        s_params['S22']['imag'] = s22_mag * np.sin(np.radians(s22_phase))
    
    elif format_str == "RI":
        # RI format: real and imaginary parts
        s11_real = data_array[:, 1]
        s11_imag = data_array[:, 2]
        s21_real = data_array[:, 3]
        s21_imag = data_array[:, 4]
        s12_real = data_array[:, 5]
        s12_imag = data_array[:, 6]
        s22_real = data_array[:, 7]
        s22_imag = data_array[:, 8]
        
        # Store real and imaginary parts
        s_params['S11']['real'] = s11_real
        s_params['S11']['imag'] = s11_imag
        s_params['S21']['real'] = s21_real
        s_params['S21']['imag'] = s21_imag
        s_params['S12']['real'] = s12_real
        s_params['S12']['imag'] = s12_imag
        s_params['S22']['real'] = s22_real
        s_params['S22']['imag'] = s22_imag
        
        # Calculate magnitude and phase
        s11_mag = np.sqrt(s11_real**2 + s11_imag**2)
        s11_phase = np.degrees(np.arctan2(s11_imag, s11_real))
        s21_mag = np.sqrt(s21_real**2 + s21_imag**2)
        s21_phase = np.degrees(np.arctan2(s21_imag, s21_real))
        s12_mag = np.sqrt(s12_real**2 + s12_imag**2)
        s12_phase = np.degrees(np.arctan2(s12_imag, s12_real))
        s22_mag = np.sqrt(s22_real**2 + s22_imag**2)
        s22_phase = np.degrees(np.arctan2(s22_imag, s22_real))
        
        # Convert magnitude to dB for plotting
        s_params['S11']['mag'] = 20 * np.log10(s11_mag)
        s_params['S11']['phase'] = s11_phase
        s_params['S21']['mag'] = 20 * np.log10(s21_mag)
        s_params['S21']['phase'] = s21_phase
        s_params['S12']['mag'] = 20 * np.log10(s12_mag)
        s_params['S12']['phase'] = s12_phase
        s_params['S22']['mag'] = 20 * np.log10(s22_mag)
        s_params['S22']['phase'] = s22_phase
    
    return freq, s_params

def plot_s_parameters(freq, s_params, title=None):
    """
    Create plots for S-parameters
    """
    # Create a figure with 4 subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"S-Parameters Analysis {title if title else ''}", fontsize=16)
    
    # Plot S11 (Magnitude and Phase)
    axs[0, 0].plot(freq, s_params['S11']['mag'], 'b-', linewidth=2)
    axs[0, 0].set_title('S11 - Magnitude (dB)')
    axs[0, 0].set_xlabel('Frequency (MHz)')
    axs[0, 0].set_ylabel('Magnitude (dB)')
    axs[0, 0].grid(True)
    
    # twin_ax = axs[0, 0].twinx()
    # twin_ax.plot(freq, s_params['S11']['phase'], 'r--', linewidth=1.5)
    # twin_ax.set_ylabel('Phase (degrees)', color='r')
    # twin_ax.tick_params(axis='y', labelcolor='r')
    
    # Plot S21 (Magnitude and Phase)
    axs[0, 1].plot(freq, s_params['S21']['mag'], 'b-', linewidth=2)
    axs[0, 1].set_title('S21 - Magnitude (dB)')
    axs[0, 1].set_xlabel('Frequency (MHz)')
    axs[0, 1].set_ylabel('Magnitude (dB)')
    axs[0, 1].grid(True)
    
    # twin_ax = axs[0, 1].twinx()
    # twin_ax.plot(freq, s_params['S21']['phase'], 'r--', linewidth=1.5)
    # twin_ax.set_ylabel('Phase (degrees)', color='r')
    # twin_ax.tick_params(axis='y', labelcolor='r')
    
    # Plot S12 (Magnitude and Phase)
    axs[1, 0].plot(freq, s_params['S12']['mag'], 'b-', linewidth=2)
    axs[1, 0].set_title('S12 - Magnitude (dB)')
    axs[1, 0].set_xlabel('Frequency (MHz)')
    axs[1, 0].set_ylabel('Magnitude (dB)')
    axs[1, 0].grid(True)
    
    # twin_ax = axs[1, 0].twinx()
    # twin_ax.plot(freq, s_params['S12']['phase'], 'r--', linewidth=1.5)
    # twin_ax.set_ylabel('Phase (degrees)', color='r')
    # twin_ax.tick_params(axis='y', labelcolor='r')
    
    # Plot S22 (Magnitude and Phase)
    axs[1, 1].plot(freq, s_params['S22']['mag'], 'b-', linewidth=2)
    axs[1, 1].set_title('S22 - Magnitude (dB)')
    axs[1, 1].set_xlabel('Frequency (MHz)')
    axs[1, 1].set_ylabel('Magnitude (dB)')
    axs[1, 1].grid(True)
    
    # twin_ax = axs[1, 1].twinx()
    # twin_ax.plot(freq, s_params['S22']['phase'], 'r--', linewidth=1.5)
    # twin_ax.set_ylabel('Phase (degrees)', color='r')
    # twin_ax.tick_params(axis='y', labelcolor='r')
    
    plt.tight_layout()
    fig.subplots_adjust(top=0.9)
    plt.show()

def main():
    # Create a simple GUI for file selection
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # # Ask user if they want to use an example file or select their own
    # use_example = input("Do you want to use the example S2P data? (y/n): ").lower().strip() == 'y'
    
    # if use_example:
    #     # Save example data to a temporary file
    #     import tempfile
    #     import os
    #     temp_dir = tempfile.gettempdir()
    #     example_file = os.path.join(temp_dir, "example_s2p_data.s2p")
    #     save_example_s2p_file(example_file)
    #     file_path = example_file
    # else:
        # Prompt for file selection
    print("Please select an S2P file.")
    file_path = filedialog.askopenfilename(
        title="Select S2P File",
        filetypes=[("S2P files", "*.s2p"), ("All files", "*.*")]
        )
    
    if not file_path:
        print("No file selected. Exiting.")
        return
    
    try:
        # Parse the S2P file
        freq, s_params = parse_s2p_file(file_path)
        
        # Plot the S-parameters
        title = f"File: {file_path.split('/')[-1]}"
        plot_s_parameters(freq, s_params, title)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()