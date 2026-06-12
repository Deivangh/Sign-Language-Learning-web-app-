# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 20:47:16 2025

@author: Deivangh
"""

import os
import subprocess

# Path to folder containing your videos
VIDEO_FOLDER = r"D:\python programs\deaf-sign-book\videos" 

# Trim duration (in seconds)
TRIM_LENGTH = 3

# Loop through all files in the folder
for filename in os.listdir(VIDEO_FOLDER):
    if filename.endswith(".mp4"):
        input_path = os.path.join(VIDEO_FOLDER, filename)
        
        # Create output filename (e.g., apple.mp4)
        output_name = filename.replace("_full", "")
        output_path = os.path.join(VIDEO_FOLDER, output_name)

        # FFmpeg command to trim first 3 seconds
        command = [
            "ffmpeg",
            "-y",                   # Overwrite output if exists
            "-i", input_path,
            "-ss", "0",
            "-t", str(TRIM_LENGTH),
            "-c", "copy",           # Fast copy without re-encoding
            output_path
        ]

        print(f"Trimming {filename} → {output_name}...")
        subprocess.run(command)

print("✅ All videos trimmed.")
