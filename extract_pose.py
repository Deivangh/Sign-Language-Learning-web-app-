# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 12:33:36 2026

@author: Deivangh
"""

import cv2
import mediapipe as mp
import json
import os

# Initialize MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic()

# Folder containing sign videos
video_folder = "videos"

# Folder where pose JSON files will be saved
output_folder = "poses"
os.makedirs(output_folder, exist_ok=True)

# Loop through all videos
for filename in os.listdir(video_folder):

    if filename.endswith(".mp4"):

        video_path = os.path.join(video_folder, filename)
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"❌ Could not open {filename}")
            continue

        frames_data = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)

            frame_landmarks = {}

            if results.left_hand_landmarks:
                frame_landmarks["left_hand"] = [
                    [lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark
                ]

            if results.right_hand_landmarks:
                frame_landmarks["right_hand"] = [
                    [lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark
                ]

            if frame_landmarks:
                frames_data.append(frame_landmarks)

        cap.release()

        # Save JSON file
        word = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{word}_pose.json")

        with open(output_path, "w") as f:
            json.dump(frames_data, f)

        print(f"✅ Pose extracted for {filename}")

print("🎉 All videos processed!")