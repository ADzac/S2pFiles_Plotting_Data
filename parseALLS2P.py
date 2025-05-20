import os
import numpy as np
import glob
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import re

s2p_files = []  # List to store S2P file paths

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
    format_str = "DB"  # Default format
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
        raise ValueError(f"No valid data found in the file: {file_path}")
    
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

def batch_parse_s2p_files(folder_path, file_pattern="*.s2p"):
    """
    Parse all S2P files in the specified folder.
    
    Parameters:
    - folder_path: path to the folder containing S2P files
    - file_pattern: pattern to match S2P files (default: "*.s2p")
    
    Returns:
    - results: dictionary with filenames as keys and (freq, s_params) tuples as values
    """
    # Check if folder exists
    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")
    
    # Find all S2P files in the folder
    search_pattern = os.path.join(folder_path, file_pattern)
    s2p_files = glob.glob(search_pattern)
    
    # Check if any files were found
    if not s2p_files:
        print(f"No S2P files found in {folder_path} with pattern {file_pattern}")
        return {}
    
    # Process each file
    results = {}

    # Step 1: Extract filenames
    filenames = [os.path.basename(p) for p in s2p_files]

    # Step 2: Sorting key
    def sort_key(fname):
        match = re.match(r"([\d.]+)m\.s2p", fname)
        return float(match.group(1)) if match else float('inf')

    # Step 3: Sort filenames
    sorted_filenames = sorted(filenames, key=sort_key)

    # Step 4: Sort original paths using sorted filename order
    s2p_files = sorted(s2p_files, key=lambda p: sorted_filenames.index(os.path.basename(p)))
    
    # Step 5: Process each file
    for file_path in s2p_files:
        try:
            # Get the filename
            filename = os.path.basename(file_path)
            
            # Parse the file
            freq, s_params = parse_s2p_file(file_path)
            
            # Store the results
            results[filename] = {
                'freq': freq,
                's_params': s_params,
                'file_path': file_path
            }
            
            print(f"Successfully parsed: {filename}")
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
    
    print(f"Processed {len(results)} files successfully out of {len(s2p_files)} total files")
    return results,s2p_files

# Example usage:
if __name__ == "__main__":
    def browse_folder():
        folder_path = filedialog.askdirectory(title="Select Folder Containing S2P Files")
        if folder_path:
            folder_path_var.set(folder_path)
    
    def process_files():
        folder = folder_path_var.get()
        pattern = pattern_var.get()
        
        if not folder:
            messagebox.showerror("Error", "Please select a folder first")
            return
        
        status_var.set("Processing files...")
        status_label.update()
        
        try:
            results,s2p_files = batch_parse_s2p_files(folder, pattern)

            if results:
                status_var.set(f"Processed {len(results)} files successfully")
                
                # Clear and update the listbox with filenames
                files_listbox.delete(0, tk.END)
                s2p_files = [os.path.basename(p) for p in s2p_files]
                for filename in s2p_files:
                    files_listbox.insert(tk.END, filename)
                
                # Store results for later use
                app.results = results
            else:
                status_var.set(f"No S2P files found in the selected folder")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            status_var.set("Error occurred during processing")
    
    def display_file_info(event=None):
        selection = files_listbox.curselection()
        if not selection:
            return
        
        filename = files_listbox.get(selection[0])
        file_data = app.results[filename]
        
        # Display file information
        info_text = f"File: {filename}\n"
        info_text += f"Path: {file_data['file_path']}\n"
        info_text += f"Frequency range: {file_data['freq'][0]:.2e} to {file_data['freq'][-1]:.2e} Hz\n"
        info_text += f"Number of points: {len(file_data['freq'])}"
        
        file_info_var.set(info_text)
        
        # Enable plot buttons
        plot_magnitude_btn.config(state=tk.NORMAL)
        plot_phase_btn.config(state=tk.NORMAL)

    # Define marker frequencies
    marker_freqs = [433, 868]  # MHz
    
    
      # circle and square

    # Helper function to add markers to a plot
    def add_markers(ax, freq_data, mag_data,marker_names = ['S12 - 433 MHz', 'S12 - 868 MHz'],marker_styles = ['o', 's'],marker_colors = ['g', 'm']):
        for i, marker_freq in enumerate(marker_freqs):
            # Find the closest frequency point
            idx = np.abs(freq_data - marker_freq).argmin()
            actual_freq = freq_data[idx]
            mag_value = mag_data[idx]
            
            # Add marker on magnitude plot
            ax.plot(actual_freq, mag_value, marker=marker_styles[i], color=marker_colors[i], 
                   markersize=8, label=f'{marker_names[i]}: {mag_value:.2f} dB')
            ax.annotate(f'{mag_value:.2f} dB', 
                       xy=(actual_freq, mag_value),
                       xytext=(10, 10), textcoords='offset points',
                       color=marker_colors[i], fontweight='bold')


    def plot_magnitude():
        selection = files_listbox.curselection()
        if not selection:
            return
        
        filename = files_listbox.get(selection[0])
        file_data = app.results[filename]
        
        freq = file_data['freq']
        s_params = file_data['s_params']
        
        # Create a new toplevel window for the plot
        plot_window = tk.Toplevel(app)
        plot_window.title(f"Magnitude Plot - {filename}")
        plot_window.geometry("1200x1000")
        
        # Create figure and canvas
        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Plot the magnitude data
        ax.plot(freq, s_params['S11']['mag'], label='S11')
        ax.plot(freq, s_params['S21']['mag'], label='S21')
        ax.plot(freq, s_params['S12']['mag'], label='S12')
        ax.plot(freq, s_params['S22']['mag'], label='S22')

        add_markers(ax, freq, s_params['S12']['mag'])
        add_markers(ax, freq, s_params['S21']['mag'],['S21 - 433 MHz', 'S21 - 868 MHz'],['H', '*'],['b', 'r'])
        
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Magnitude (dB)')
        ax.set_title(f'S-Parameters Magnitude - {filename}')
        ax.grid(True)
        ax.legend()
        
        canvas.draw()
    
    def plot_phase():
        selection = files_listbox.curselection()
        if not selection:
            return
        
        filename = files_listbox.get(selection[0])
        file_data = app.results[filename]
        
        freq = file_data['freq']
        s_params = file_data['s_params']
        
        # Create a new toplevel window for the plot
        plot_window = tk.Toplevel(app)
        plot_window.title(f"Phase Plot - {filename}")
        plot_window.geometry("800x600")
        
        # Create figure and canvas
        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Plot the phase data
        ax.plot(freq, s_params['S11']['phase'], label='S11')
        ax.plot(freq, s_params['S21']['phase'], label='S21')
        ax.plot(freq, s_params['S12']['phase'], label='S12')
        ax.plot(freq, s_params['S22']['phase'], label='S22')
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase (degrees)')
        ax.set_title(f'S-Parameters Phase - {filename}')
        ax.grid(True)
        ax.legend()
        
        canvas.draw()
    
    def find_closest_freq_index(freq_array, target_freq):
        """Find the index of the closest frequency to the target in the frequency array"""
        return np.abs(freq_array - target_freq).argmin()
    
    def plot_corrected_s21_vs_distance():
        """Plot corrected S21 values (normalized with reference) vs distance for each frequency"""
        if not hasattr(app, 'results') or not app.results:
            messagebox.showinfo("Info", "Please process files first")
            return

        # Reference S21 values
        ref_data = app.results.get("ref.s2p")
        if not ref_data:
            messagebox.showwarning("Warning", "Reference file 'ref.s2p' not found")
            return

        ref_freqs = ref_data['freq']
        ref_s21 = ref_data['s_params']['S21']['mag']

        target_freqs = {
            "433 MHz": 433,
            "868 MHz": 868
        }

        distances = []
        corrected_values = {
            "433 MHz": [],
            "868 MHz": []
        }

        for filename, file_data in app.results.items():
            if filename == "ref.s2p":
                continue  # Skip reference file

            # Extract distance from filename (e.g., "0.35m.s2p")
            match = re.match(r"([\d.]+)m\.s2p", filename)
            if not match:
                continue  # Skip files that don't match the pattern

            distance = float(match.group(1))
            distances.append(distance)

            freqs = file_data['freq']
            s21 = file_data['s_params']['S21']['mag']

            for label, f in target_freqs.items():
                idx = find_closest_freq_index(freqs, f)
                ref_idx = find_closest_freq_index(ref_freqs, f)

                corrected_s21 = s21[idx] - ref_s21[ref_idx]
                corrected_values[label].append(corrected_s21)

        # Sort data by distance
        sorted_data = sorted(zip(distances, corrected_values["433 MHz"], corrected_values["868 MHz"]))
        distances_sorted, s21_433, s21_868 = zip(*sorted_data)

        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(distances_sorted, s21_433, marker='o', label="433 MHz")
        plt.plot(distances_sorted, s21_868, marker='s', label="868 MHz")

        plt.title("Corrected S21 vs Distance")
        plt.xlabel("Distance (m)")
        plt.ylabel("Corrected S21 (dB)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def create_freq_comparison_table():
        """Create a table comparing S-parameters at specific frequencies for all files"""
        if not hasattr(app, 'results') or not app.results:
            messagebox.showinfo("Info", "Please process files first")
            return

        # Target frequencies in Hz
        target_freqs = {
            "433 MHz": 433,
            "868 MHz": 868
        }
        
        # Create a new window for the comparison table
        table_window = tk.Toplevel(app) 
        table_window.title("Frequency Comparison Table")
        table_window.geometry("1200x1000")
        
        # Create a frame for the table
        frame = ttk.Frame(table_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create DataFrame to store the results
        data = []
        
        # Collect data for each file
        for filename, file_data in app.results.items():
            freq = file_data['freq']
            s_params = file_data['s_params']
            
            file_row = {"Filename": filename}
            
            # For each target frequency
            for freq_name, freq_value in target_freqs.items():
                # Find the closest frequency in the data
                idx = find_closest_freq_index(freq, freq_value)
                
                # Store the actual frequency found and S-parameter values
                file_row[f"{freq_name} S12 (dB)"] = f"{s_params['S12']['mag'][idx]:.2f}"
                file_row[f"{freq_name} S21 (dB)"] = f"{s_params['S21']['mag'][idx]:.2f}"
            
            data.append(file_row)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)

        def extract_numeric_value(filename):
            # Extract the numeric part before 'm.s2p'
            match = re.match(r"([\d.]+)m\.s2p", filename)
            if match:
                return float(match.group(1))
            return float('inf')  # Default high value for non-matching files
        
        # Sort by numeric value in filename
        df['sort_key'] = df['Filename'].apply(extract_numeric_value)
        df = df.sort_values("sort_key")
        df = df.drop('sort_key', axis=1)  # Remove the temporary sort column
        
        # Create the table
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = list(df.columns)
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack scrollbars and treeview
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        # Add data to treeview
        for _, row in df.iterrows():
            values = [row[col] for col in columns]
            tree.insert("", "end", values=values)
        
        # Add buttons frame
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=10)

        plot_corrected_s21_vs_distance()

    # Create the main window
    app = tk.Tk()
    app.title("S2P File Batch Processor")
    app.geometry("800x600")
    app.results = {}  # Will store the parsed results
    
    # Create variables
    folder_path_var = tk.StringVar()
    pattern_var = tk.StringVar(value="*.s2p")
    status_var = tk.StringVar(value="Ready")
    file_info_var = tk.StringVar(value="Select a file to view details")
    
    # Create main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Folder selection frame
    folder_frame = ttk.LabelFrame(main_frame, text="Folder Selection", padding="5")
    folder_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(folder_frame, text="Folder:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(folder_frame, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(folder_frame, text="Browse...", command=browse_folder).grid(row=0, column=2, padx=5, pady=5)
    
    ttk.Label(folder_frame, text="File Pattern:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(folder_frame, textvariable=pattern_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    ttk.Button(folder_frame, text="Process Files", command=process_files).grid(row=1, column=2, padx=5, pady=5)
    
    # Comparison table button
    ttk.Button(folder_frame, text="Frequency Comparison Table", command=create_freq_comparison_table).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Status bar
    status_label = ttk.Label(main_frame, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    # Results frame
    results_frame = ttk.Frame(main_frame)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Split into left and right panels
    left_panel = ttk.Frame(results_frame)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    right_panel = ttk.Frame(results_frame)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
    
    # Files list in left panel
    ttk.Label(left_panel, text="S2P Files:").pack(anchor=tk.W)
    files_frame = ttk.Frame(left_panel)
    files_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(files_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    files_listbox = tk.Listbox(files_frame)
    files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    files_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=files_listbox.yview)
    files_listbox.bind('<<ListboxSelect>>', display_file_info)
    
    # File info in right panel
    info_frame = ttk.LabelFrame(right_panel, text="File Information")
    info_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(info_frame, textvariable=file_info_var, justify=tk.LEFT, wraplength=350).pack(padx=10, pady=10, anchor=tk.W)
    
    # Plot buttons
    buttons_frame = ttk.Frame(right_panel)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    plot_magnitude_btn = ttk.Button(buttons_frame, text="Plot Magnitude", command=plot_magnitude, state=tk.DISABLED)
    plot_magnitude_btn.pack(side=tk.LEFT, padx=5)
    
    plot_phase_btn = ttk.Button(buttons_frame, text="Plot Phase", command=plot_phase, state=tk.DISABLED)
    plot_phase_btn.pack(side=tk.LEFT, padx=5)
    
    # Start the main loop
    app.mainloop()