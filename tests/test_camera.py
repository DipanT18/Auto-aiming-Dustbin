"""
This script tests the functionality of the camera input for the Auto-aiming-Dustbin project.

Usage Instructions:
1. Run the script using Python 3.
2. Ensure your camera is connected and accessible.
3. The script will display the camera feed and output test results.
4. Press 'q' to quit the live feed.
"""

import cv2
import time
import numpy as np
from termcolor import colored

# Camera settings
def test_camera():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print(colored("ERROR: Camera not found!", 'red'))
        return False

    # Get expected resolution
    expected_width = 1280
    expected_height = 720
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, expected_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, expected_height)

    # Measure actual FPS
    start_time = time.time()
    frame_count = 0
    total_time = 0
    print(colored("Press 'q' to quit", 'yellow'))

    while True:
        ret, frame = camera.read()
        if not ret:
            print(colored("ERROR: Could not read frame!", 'red'))
            break

        # Calculate frame resolution
        height, width, _ = frame.shape

        # Check resolution
        if (width, height) != (expected_width, expected_height):
            print(colored("WARNING: Frame resolution is not as expected!", 'yellow'))

        # Display live feed
        cv2.imshow('Live Camera Feed', frame)
        frame_count += 1

        # Handle quitting
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Measure frame processing time
        total_time += time.time() - start_time
        start_time = time.time()

    camera.release()
    cv2.destroyAllWindows()

    # Calculate FPS and frame quality metrics
    actual_fps = frame_count / total_time if total_time > 0 else 0
    print(colored(f"Captured {frame_count} frames at an actual FPS of {actual_fps:.2f}", 'green'))
    if actual_fps < 10:
        print(colored("WARNING: FPS is lower than expected!", 'yellow'))
    else:
        print(colored("PASS: Camera test completed successfully!", 'green'))

# Run the camera test
if __name__ == '__main__':
    test_camera()