# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 21:35:34 2025

@author: Deivangh
"""


import os
import json

# Define the path to the video folder and output JSON
base_path = r"D:\python programs\deaf-sign-book"
video_folder = os.path.join(base_path, "videos")
output_file = os.path.join(base_path, "mapping.json")

# Create mapping dictionary
mapping = {}

# Loop through video files
for filename in os.listdir(video_folder):
    if filename.endswith(".mp4"):
        word = os.path.splitext(filename)[0].lower()
        mapping[word] = os.path.join("videos", filename)  # Relative path

# Save to mapping.json
with open(output_file, "w") as f:
    json.dump(mapping, f, indent=4)

print(f"✅ mapping.json created with {len(mapping)} entries.")


'''
import os
import json

# Folder containing trimmed videos
VIDEO_FOLDER = r"D:\python programs\deaf-sign-book\videos"

# Output file
OUTPUT_FILE = os.path.join(VIDEO_FOLDER, "mapping.json")

# Create dictionary
mapping = {}

# Loop through trimmed videos (exclude *_full.mp4)
for file in os.listdir(VIDEO_FOLDER):
    if file.endswith(".mp4") and not file.endswith("_full.mp4"):
        key = file.replace(".mp4", "")  # e.g., "apple"
        mapping[key] = f"videos/{file}"

# Save as mapping.json
with open(OUTPUT_FILE, "w") as f:
    json.dump(mapping, f, indent=4)

print(f"✅ mapping.json created with {len(mapping)} entries.")
'''