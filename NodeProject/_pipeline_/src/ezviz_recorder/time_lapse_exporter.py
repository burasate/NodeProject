# -*- coding: utf-8 -*-
import os, subprocess, time, datetime, sys, shutil
print('__name__', __name__)
print('__file__', __file__)

base_dir = os.path.dirname(os.path.abspath(__file__))
if not base_dir in sys.path:
    sys.path.insert(0, base_dir)

import config
captures_dir =os.path.dirname(__file__) + '/captures'
print(captures_dir)
print(config.ffmpeg_path)

def images_to_mp4(image_folder, output_file, ffmpeg_path="ffmpeg", fps=60, bitrate="900k"):
    """
    Convert a sequence of images in a folder to an MP4 video with a custom bitrate.

    :param image_folder: Path to the folder containing the images
    :param output_file: Output MP4 file path
    :param ffmpeg_path: Path to the ffmpeg executable (default is "ffmpeg")
    :param fps: Frames per second for the video
    :param bitrate: Target video bitrate (e.g., '2500k' for 2500 Kbps)
    """
    # Make sure the folder exists
    if not os.path.isdir(image_folder):
        raise FileNotFoundError(f"Folder not found: {image_folder}")

    # Verify if ffmpeg is accessible from the provided path
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")

    # Create a temporary folder for the renamed images
    temp_folder = os.path.join(image_folder, "temp_images")
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    # Get and sort the .jpg images in the folder
    image_files = sorted(
        [f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")],
        key=lambda x: x  # Lexicographical sorting (timestamps will naturally sort this way)
    )

    # Filter out images that are less than 1 byte in size and remove them
    for f in image_files:
        file_path = os.path.join(image_folder, f)
        if os.path.getsize(file_path) < 2:  # Filter files less than 2 bytes (to be safe)
            print(f"Removing {f} due to its size: {os.path.getsize(file_path)} bytes")
            os.remove(file_path)

    [f for f in os.listdir(image_folder) if os.path.exists(os.path.join(image_folder, f))]

    if not image_files:
        raise FileNotFoundError(f"No .jpg images found in the folder: {image_folder}")

    # Rename and copy the images to the temp folder as %04d.jpg
    for idx, img in enumerate(image_files, start=1):
        img_path = os.path.join(image_folder, img)
        if os.path.isfile(img_path):
            # Format the filename to %04d.jpg (e.g., 0001.jpg, 0002.jpg)
            new_name = f"{idx:04d}.jpg"
            shutil.copy(img_path, os.path.join(temp_folder, new_name))

    # Ensure that we are correctly naming and processing all images
    image_files_in_temp = sorted(
        [f for f in os.listdir(temp_folder) if f.lower().endswith(".jpg")],
        key=lambda x: int(x.split('.')[0])  # Sorting the newly renamed images numerically
    )

    # Ensure that there are valid files left after filtering
    if not image_files_in_temp:
        raise Exception(f"No valid images found after filtering.")

    # Use ffmpeg to convert the renamed images to a video with a custom bitrate
    command = [
        ffmpeg_path,  # Use the specified ffmpeg path
        "-y",  # Overwrite output file without asking
        "-framerate", str(fps),  # Set frame rate
        "-i", os.path.join(temp_folder, "%04d.jpg"),  # Input file pattern (e.g., 0001.jpg, 0002.jpg)
        "-c:v", "libx265",  # Use H.264 codec
        "-preset", "medium",  # Use the highest quality preset
        "-crf", "23",  # Constant rate factor (0 = lossless, lower = better quality)
        "-pix_fmt", "yuv420p",  # Pixel format for compatibility
        "-b:v", bitrate,  # Set the custom video bitrate (e.g., 2500k for 2500 Kbps)
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error while creating video: {e}")

    # Cleanup: remove the temporary folder
    shutil.rmtree(temp_folder)

today_str = datetime.datetime.today().strftime('%Y%m%d')
cam_dir_ls = [captures_dir + os.sep + i for i in os.listdir(captures_dir)]
for cam_dir in cam_dir_ls:
    seq_dir = cam_dir + os.sep + 'img_sequences'
    #print(seq_dir)
    date_str_ls = list(set([i.split('_')[1] for i in os.listdir(seq_dir)]))
    #print(date_str_ls)
    for date_str in date_str_ls:
        if date_str == today_str:
            continue

        img_file_ls = sorted([i for i in os.listdir(seq_dir) if date_str in i])
        mp4_path = cam_dir + os.sep + os.path.basename(cam_dir) + '_' + date_str + '.mp4'

        temp_date_seq_dir = cam_dir + os.sep + date_str + '_tmp'
        if os.path.exists(temp_date_seq_dir):
            shutil.rmtree(temp_date_seq_dir, ignore_errors=True)
        elif not os.path.exists(mp4_path):
            os.makedirs(temp_date_seq_dir, exist_ok=True)

        if os.path.exists(mp4_path):
            [os.remove(seq_dir + os.sep + i) for i in img_file_ls]
            continue
        else:
            [shutil.copy(seq_dir + os.sep + i, temp_date_seq_dir + os.sep + i) for i in img_file_ls]
            ffmpeg_path = config.ffmpeg_path
            images_to_mp4(temp_date_seq_dir, mp4_path, ffmpeg_path)

        shutil.rmtree(temp_date_seq_dir, ignore_errors=True)

# Example usage
#image_folder = r"C:\Users\DEX3D_I7\Desktop\captures"  # Replace with the folder containing images
#output_file = r"C:\Users\DEX3D_I7\Desktop\captures.mp4"  # Replace with your desired output file name
#ffmpeg_path = r"D:\GDrive\Documents\2022\BRSAnimPipeline\work\NodeProject\NodeProject\_pipeline_\src\ffmpeg\bin\ffmpeg.exe"  # Specify the full path to ffmpeg.exe
#images_to_mp4(image_folder, output_file, ffmpeg_path)


