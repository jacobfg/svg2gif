#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
from PIL import Image
import os
import time
import argparse

def clear_frames_dir(frames_dir):
    """Clear all files in the frames directory."""
    if os.path.exists(frames_dir):
        for file in os.listdir(frames_dir):
            file_path = os.path.join(frames_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"Cleared the frames directory: {frames_dir}")
    else:
        os.makedirs(frames_dir)
        print(f"Created frames directory: {frames_dir}")

def extract_frames(input_svg_path, num_frames, frame_duration, frames_dir):
    """Extract frames from an animated SVG and save as PNG files."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load SVG content
        with open(input_svg_path, 'r') as file:
            svg_content = file.read()
        page.set_content(f'<html><body>{svg_content}</body></html>')

        for i in range(num_frames):
            time.sleep(frame_duration / 1000)  # Wait for the duration of the frame
            frame_path = os.path.join(frames_dir, f'frame_{i}.png')
            page.screenshot(path=frame_path, full_page=True)
            print(f'Captured frame {i}')

        browser.close()

def create_gif(output, frame_duration, frames_dir):
    """Create a GIF from the extracted PNG frames."""
    frame_files = sorted(
        [f for f in os.listdir(frames_dir) if f.endswith('.png')],
        key=lambda x: int(x.split('_')[1].split('.')[0])
    )
    
    frames = [Image.open(os.path.join(frames_dir, file)) for file in frame_files]

    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration/10,
        loop=0
    )
    
    print(f'GIF saved to {output}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs=1, type=str)
    parser.add_argument('output', nargs=1, type=str)
    parser.add_argument('-f', '--frames', type=int, help='frames', default=12, required=False)
    parser.add_argument('-t', '--frame-duration', type=int, help='frame_duration', default=1000, required=False)
    parser.add_argument('-d', '--frame-directory', type=str, help='frame_directory', default='frames', required=False)
    parsed_args = parser.parse_args()

    input = parsed_args.input[0]
    output = parsed_args.output[0]

    clear_frames_dir(parsed_args.frame_directory)
    extract_frames(input, parsed_args.frames, parsed_args.frame_duration, parsed_args.frame_directory)
    create_gif(output, parsed_args.frame_duration, parsed_args.frame_directory)
