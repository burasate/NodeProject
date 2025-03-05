# -*- coding: utf-8 -*-
import os, subprocess, time, datetime, sys, traceback
print('__name__', __name__)
print('__file__', __file__)

base_dir = os.path.dirname(os.path.abspath(__file__))
if not base_dir in sys.path:
    sys.path.insert(0, base_dir)

import config
captures_dir =os.path.dirname(__file__) + '/captures'
print(captures_dir)

class util:
    @staticmethod
    def get_ssid_name():
        os_name = os.name
        if os_name == 'nt':  # windows
            ssid_encode = subprocess.check_output("netsh wlan show interfaces")
            ssid_decode = ssid_encode.decode().strip()
            print(ssid_decode)
            ssid_find = [i.strip() for i in ssid_decode.split('\n')]
            ssid_find = [i for i in ssid_find if i.startswith('SSID')]
            if ssid_find:
                ssid = ssid_find[0].split(':')[-1].strip()
                return ssid
            else:
                raise Warning('can\'t found ssid or wlan is disconnected')
        elif os_name == 'posix':  # raspberry pi
            ssid_encode = subprocess.check_output("iwgetid")
            ssid_decode = ssid_encode.decode().strip()
            print(ssid_decode)
            ssid_find = [i.strip() for i in ssid_decode.split('\n')]
            ssid_find = [i for i in ssid_find if 'SSID' in i]
            if ssid_find:
                ssid = ssid_find[0].split(':')[-1].strip().replace('\"', '')
                return ssid
            else:
                raise Warning('can\'t found ssid or wlan is disconnected')

while util.get_ssid_name() != config.ssid:
    print('Warning\nWifi name doesn\'t match with config file')
    time.sleep(180)

print('camera registeration list..')
for i in config.reg_local_ip_ls:
    print(i)
print('----------')

st_time = time.time()
duration = config.interval + 1.0
while True:
    if duration >= config.interval:
        os.system('cls||clear')
        for idx, (ch, pw, ip) in enumerate(config.reg_local_ip_ls):
            name = 'CAM{0:02d}'.format(int(ch))
            rtsp_url = "rtsp://admin:{}@{}:554".format(pw, ip)
            cam_dir = captures_dir + os.sep + name + os.sep + 'img_sequences'
            if not os.path.exists(cam_dir):
                os.makedirs(cam_dir, exist_ok=1)
            else:
                img_path_ls = [cam_dir + os.sep + i for i in os.listdir(cam_dir)]
                if len(img_path_ls) > config.files_limit:
                    last_img_path_ls = img_path_ls[-config.files_limit:]
                    [os.remove(i) for i in img_path_ls if i not in last_img_path_ls] # clamp files count
                    del img_path_ls, last_img_path_ls

            now_format = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            img_path = cam_dir + os.sep + '{}_'.format(name) + now_format + '.jpg'

            ffmpeg_command = [
                config.ffmpeg_path,  # Path to the FFmpeg executable
                "-rtsp_transport", "udp",  # Use UDP (can be more stable in some networks)
                "-i", rtsp_url,  # Input RTSP stream URL
                "-buffer_size", "8192000",  # Set buffer size to 8MB to prevent packet loss
                "-an",  # Disable audio (reduces processing and potential errors)
                # "-frames:v", "1",  # (Optional) Capture a single frame instead of a short clip
                "-t", "5",  # Capture 2 seconds of video
                "-r", "14",  # Set FPS to 14 (match the stream's FPS if needed)
                "-update", "1",  # Overwrite the same image file instead of creating new ones (for image output)
                "-q:v", "2",  # Set image quality (lower values are better, 2 is nearly lossless)
                "-y",  # Overwrite output file if it exists
                img_path  # Path where the output image/video will be saved
            ]
            try:
                result = subprocess.run(ffmpeg_command, check=False, timeout=config.ffmpeg_timeout,
                                        capture_output=True, text=True)

                stderr = str(result.stderr).strip()
                print(stderr[-100:])

                if 'failed:' in stderr:
                    raise Warning('Cannot connect to camera... {}  {}'.format(name, rtsp_url))
                else:
                    print("{} {}  Picture saved successfully.\n\n".format(name, now_format))
            except Exception as e:
                print('\n==========================\n')
                print(str(traceback.format_exc()))
                print('\n==========================\n')
                continue

    # update interval
    en_time = time.time()
    duration = en_time - st_time
    if duration > config.interval:
        st_time = time.time()