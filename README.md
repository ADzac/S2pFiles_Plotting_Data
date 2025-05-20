S2P File Parsing and Visualization Tools
This repository contains three Python programs for parsing and visualizing S2P files (Touchstone format) containing S-parameter data. Each program serves a different purpose and offers varying levels of functionality.

Programs Overview
1. parseS2p.py
Basic S2P file parser and visualizer

Features:

Single file processing

Parses S2P files in DB, MA, or RI formats

Displays magnitude plots for all S-parameters (S11, S12, S21, S22)

Simple GUI for file selection

2. parseS2pV2.py
Enhanced version with frequency markers

Additional features beyond parseS2p.py:

Automatic markers at 433MHz and 868MHz frequencies

Displays actual values at marker frequencies

Better visualization with legends and annotations

Checks if marker frequencies are within the data range

3. parseALLS2P.py
Batch processing tool with advanced features

Additional features beyond parseS2pV2.py:

Processes multiple S2P files in a folder

Automatic sorting of files by distance (from filenames)

Interactive GUI with file listing and information display

Comparison table for specific frequencies across files

Corrected S21 vs distance plotting

Reference file normalization capability

Common Features
All three programs:

Support standard S2P file formats (DB, MA, RI)

Extract and visualize S-parameter data

Handle complex numbers and convert between formats

Provide magnitude plots in dB scale

Usage Instructions
For parseS2p.py and parseS2pV2.py:
Run the script: python parseS2p.py or python parseS2pV2.py

Select an S2P file using the file dialog

View the generated plots

For parseALLS2P.py:
Run the script: python parseALLS2P.py

Use the GUI to:

Select a folder containing S2P files

Process all matching files

View individual file information

Generate magnitude or phase plots

Create comparison tables

Plot corrected S21 vs distance

File Naming Convention (for parseALLS2P.py)
For best results with parseALLS2P.py, name your files with distance information:

Example: 0.35m.s2p, 1.0m.s2p, etc.

Include a reference file named ref.s2p for corrected S21 calculations

Dependencies
Python 3.x

Required packages:

numpy

matplotlib

tkinter (usually included with Python)

pandas (for parseALLS2P.py)

Install dependencies with:

bash
pip install numpy matplotlib pandas
Notes
All programs assume frequency data is in MHz

parseALLS2P.py provides the most comprehensive analysis for batch processing

For single file analysis, parseS2pV2.py offers the best visualization

License
This code is provided as-is for educational and research purposes. Modify and use as needed.
