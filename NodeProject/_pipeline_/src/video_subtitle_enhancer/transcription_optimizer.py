# -*- coding: utf-8 -*-
'''
1. mp4 to mp3
2. mp3 to original speech text
3. speech text ai improving
4. extracted video without voice or vocal
'''
#https://ottverse.com/ffmpeg-drawtext-filter-dynamic-overlays-timecode-scrolling-text-credits/

import os, shutil, subprocess, json, sys, tempfile, time, re, math
from datetime import timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))
prev_dir = os.sep.join( os.path.join(base_dir).split(os.sep)[:-1] ) #src
site_packages_dir = prev_dir + os.sep + 'site-packages'
if '3.7' in str(sys.version):
	for p in [base_dir, site_packages_dir, prev_dir]:
		if not p in sys.path and os.path.exists(p):
			sys.path.insert(0, p)
			print(sys.path[0])

print(base_dir)
import config

#---------------------------------------------------------------------------------
class util:
	@staticmethod
	def get_rename_file_extension(file_path, ext='txt'):
		base_name = os.path.basename(file_path)
		if base_name.count('.') > 1:
			raise Warning('\".\" more than one')
		base_name = os.path.basename(file_path).split('.')[0]
		base_name += '.{}'.format(ext.replace('.', ''))
		new_path = os.path.dirname(file_path) + os.sep + base_name
		return new_path

#---------------------------------------------------------------------------------

class openai_gpt:
	def __init__(self, api_key,  model='gpt-3.5-turbo'):
		self.model = model
		import openai
		self.openai = openai
		self.openai.api_key = api_key

	def set_sys_prompt(self, msg):
		msg = msg.strip()
		for i in range(3):
			msg = msg.replace('  ', ' ').strip()
		print(sys_prompt)
		self.sys_prompt = msg

	def get_completion_response(self, msg, output_fmt='json', temperature=0.25, top_p=1.0):
		if output_fmt != 'json':
			return
		try:
			print('\nCompletion connecting...')
			completion = self.openai.ChatCompletion.create(
				model=self.model,
				messages=[
					{"role": "system", "content": self.sys_prompt},
					{"role": "user", "content": msg}
				],
				temperature=temperature,
				top_p=top_p
			)
			return completion
		except Exception as e:
			#import traceback
			#print(str(traceback.format_exc()))
			print('\n' + e.__str__() + '\n')
			time.sleep(.75)
			return None

# ---------------------------------------------------------------------------------
'''
1. convert video to audio
2. 
'''
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

import speech_recognition as sr
ffmpeg_path = os.path.join(os.path.abspath(prev_dir), 'ffmpeg', 'bin', 'ffmpeg.exe')
ffprobe_path = os.path.join(os.path.abspath(prev_dir), 'ffmpeg', 'bin', 'ffprobe.exe')

def get_width_height(video_input):
	# Use ffprobe to get video info
	ffprobe_command = [
		ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
		'-of', 'json', video_input
	]

	# Run the command and get the output
	result = subprocess.run(ffprobe_command, capture_output=True, text=True)

	# Parse the JSON output
	video_info = json.loads(result.stdout)

	# Extract the width and height
	width = video_info['streams'][0]['width']
	height = video_info['streams'][0]['height']

	print(f"Width: {width}, Height: {height}")
	return (width, height)

def seconds_to_ffmpeg_time(seconds):
    return str(timedelta(seconds=seconds))

def convert_video_to_mp3(video_path):
	if not video_path.endswith(('.mp4', '.mov')):
		return None

	mp3_path = os.path.splitext(video_path)[0] + '.mp3'

	command = [
		ffmpeg_path, '-i', video_path, '-q:a', '0', '-map', 'a', mp3_path, "-y"
	]
	subprocess.run(command, check=True)
	return mp3_path

def get_audio_duration(audio_file):
    # Using speech_recognition's AudioFile.DURATION to get the audio file's duration
    with sr.AudioFile(audio_file) as source:
        return source.DURATION

def transcribe_convert(file_path, txt_path, silen_db=-30, silen_duration=0.45):
	#if not file_path.endswith('.mp3') or not txt_path.endswith('.txt'):
		#return

	temp_dir = tempfile.gettempdir()
	wav_dir = os.path.join(temp_dir, os.path.splitext(os.path.basename(file_path))[0] + '_split')
	base_wav_path = os.path.join(wav_dir, os.path.basename(file_path).replace('.mp3', '.wav'))

	if os.path.exists(wav_dir):
		try:
			shutil.rmtree(wav_dir)
			time.sleep(3)
		except Exception as e:
			print(f"Error removing directory: {e}")

	os.makedirs(wav_dir, exist_ok=True)
	os.chmod(wav_dir, 0o777)

	# Use ffmpeg to detect silence and print timestamps of silence
	command = [
		ffmpeg_path, '-i', file_path,
		'-af', f'silencedetect=n={silen_db}dB:d={silen_duration}',  # Detect silence
		'-f', 'null',  # No output file, just to capture the silence detection logs
		'-'
	]
	result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
	silence_lines = result.stderr.splitlines()

	# Extract the silence start and end times from ffmpeg output
	silence_starts = []
	silence_ends = []

	for line in silence_lines:
		if 'silence_start' in line:
			silence_starts.append(float(line.split('silence_start: ')[1]))
		elif 'silence_end' in line:
			silence_ends.append(float(line.split('silence_end: ')[1].split(' |')[0]))

	# Now, generate split points based on silence detection
	split_points = [0.0]  # Start from the beginning of the file
	for start, end in zip(silence_starts, silence_ends):
		split_points.append(end)  # Add the end of each silence

	# Create split files based on silence points
	audio_files = []
	seg_start_ls = []
	seg_end_ls = []
	for i in range(len(split_points) - 1):
		segment_start = split_points[i]
		segment_end = split_points[i + 1]
		segment_filename = os.path.join(wav_dir, f'segment_{i:03d}.wav')
		command = [
			ffmpeg_path, '-i', file_path,
			'-ss', str(segment_start),  # Start of the segment
			'-to', str(segment_end),  # End of the segment
			'-segment_format', 'wav',  # Segment format
			segment_filename,
			'-loglevel', 'quiet'
		]
		subprocess.run(command, check=True)
		audio_files.append(segment_filename)
		seg_start_ls.append(segment_start)
		seg_end_ls.append(segment_end)

	# speech recognizer
	r = sr.Recognizer()
	sr_key = config.wit_api_key
	del_idx_ls = []
	for idx, (a_path, start, end) in enumerate(zip(audio_files, seg_start_ls, seg_end_ls)):
		start_str = '{:010.5f}'.format(start)
		end_str = '{:010.5f}'.format(end)
		print(
			f'listening.. Track {idx + 1}/{len(audio_files)} | {os.path.basename(a_path)}')

		with sr.AudioFile(a_path) as a_src:
			audio_data = r.record(a_src)
			try:
				text = r.recognize_wit(audio_data, key=sr_key)
				if text.strip():
					formatted_text = f'{os.path.basename(file_path)}|{start_str}|{end_str}|{text}'
					print(formatted_text + '\n')
				write_mode = 'x' if not os.path.exists(txt_path) else 'a'
				with open(txt_path, write_mode) as f:
					f.write(formatted_text + '\n')
			except sr.UnknownValueError:
				#print('speech_recognition.UnknownValueError\n')
				print('..unknown..\n')
				del_idx_ls.append(idx)

	audio_files = [n for i, n in enumerate(audio_files) if not i in del_idx_ls]
	seg_start_ls = [n for i, n in enumerate(seg_start_ls) if not i in del_idx_ls]
	seg_end_ls = [n for i, n in enumerate(seg_end_ls) if not i in del_idx_ls]
	#print(list(zip(audio_files, seg_start_ls, seg_end_ls)))

	# remove temp folder
	if os.path.exists(wav_dir):
		try:
			shutil.rmtree(wav_dir)
		except Exception as e:
			print(f"Error removing directory: {e}")

	# finishing new transcription file
	f_lines = open(txt_path).readlines()
	f_lines = sorted( list(set(f_lines)) )
	with open(txt_path, 'w') as f:
		f.write(''.join(f_lines))
		f.close()

def perform_text_burn_in(json_file, input_video, output_video):

	def split_txt_into_multi_lines(input_str: str, line_length: int):
		words = input_str.split(" ")
		line_count = 0
		split_input = ""
		for word in words:
			line_count += 1
			line_count += len(word)
			if line_count > line_length:
				split_input += "\n"
				line_count = len(word) + 1
				split_input += word
				split_input += " "
			else:
				split_input += word
				split_input += " "
		return split_input

	iw, ih = get_width_height(input_video)
	text_size = max(iw, ih) // 22
	text_split_size = text_size // 3 if max(iw, ih) == ih else text_size // 5
	text_split_size = min(max(text_split_size, 10), 30)
	font_path = os.path.abspath(base_dir + "/fonts/arial.ttf").replace("\\", "/")

	# Step 1: Load JSON file
	with open(json_file, 'r') as f:
		subtitles = json.load(f)

	# Step 2: Set up temp folder in the system's temp directory
	temp_dir = tempfile.gettempdir()
	temp_folder_path = os.path.join(temp_dir, 'temp_vdo_text_burnin')

	# Print the temp folder path for debugging
	print(f"Temp folder path: {temp_folder_path}")

	# Clean up temp folder if it exists
	if os.path.exists(temp_folder_path):
		try:
			shutil.rmtree(temp_folder_path)
		except Exception as e:
			print(f"Error removing directory: {e}")

	# Create temp folder and set permissions
	try:
		os.makedirs(temp_folder_path, exist_ok=True)
		os.chmod(temp_folder_path, 0o777)
	except:
		pass

	# Step 3: Separate the video clip according to the timecode in the JSON file
	clip_files = []
	subtitles_list = list(subtitles.items())
	for i, (start_time, text) in enumerate(subtitles_list):
		# Prepare the start time for FFmpeg (in the format HH:MM:SS.MS)
		hours, minutes, seconds = start_time.split(':')
		if '.' in start_time:
			seconds, milliseconds = seconds.split('.')
		else:
			seconds, milliseconds = (seconds, 0)

		text = split_txt_into_multi_lines(text, text_split_size)
		print(text)
		time.sleep(1)

		try:
			# Convert time to seconds as a float value for ffmpeg
			time_in_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + float(f"0.{milliseconds}")
		except ValueError as e:
			print(f"Error converting time {start_time}: {e}")
			continue  # Skip this entry and move to the next one

		# Get the next subtitle's start time for calculating the end time
		if i + 1 < len(subtitles_list):
			next_start_time = subtitles_list[i + 1][0]
			next_hours, next_minutes, next_seconds = next_start_time.split(':')
			next_seconds, next_milliseconds = next_seconds.split('.')
			next_time_in_seconds = int(next_hours) * 3600 + int(next_minutes) * 60 + int(next_seconds) + float(
				f"0.{next_milliseconds}")
		else:
			# If it's the last subtitle, set an arbitrary duration (e.g., 10 seconds)
			next_time_in_seconds = time_in_seconds + 10  # default duration

		# Output clip filename
		output_clip = os.path.join(temp_folder_path, f"clip_{start_time.replace(':', '').replace('.', '_')}.mp4")

		try:
			os.system('cls||clear')
			print(f"split apart: {output_clip}")
			time.sleep(1)

			# Cut the video according to the time range
			command = [
				ffmpeg_path, '-i', input_video, '-ss', str(time_in_seconds), '-to', str(next_time_in_seconds),
				'-c:v', 'libx264', '-c:a', 'copy', '-y', output_clip
			]
			subprocess.run(command, check=True)
		except subprocess.CalledProcessError as e:
			print(f"Error processing video clip for time {start_time}: {e}")
			continue  # Skip this clip and move to the next one

		# Step 4: Apply FFmpeg drawtext to burn-in the subtitle text
		output_clip_burned = os.path.join(temp_folder_path,
										  f"clip_burned_{start_time.replace(':', '').replace('.', '_')}.mp4")

		try:
			os.system('cls||clear')
			print(f"burn in subtitle: {output_clip_burned}")
			time.sleep(1)

			# Adjusting text wrapping if necessary based on video width
			drawtext_command = [
				ffmpeg_path, '-i', output_clip, '-vf',
				f"drawtext=text='{text}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize={text_size}:fontcolor=white:borderw={5}:bordercolor=black:fontfile='{font_path}'",
				'-c:a', 'copy', '-y', output_clip_burned
			]
			subprocess.run(drawtext_command, check=True)
		except subprocess.CalledProcessError as e:
			print(f"Error adding text to video for time {start_time}: {e}")
			continue  # Skip this clip and move to the next one

		# Add the processed clip to the list of clips for later concatenation
		clip_files.append(output_clip_burned)

	# Step 5: Combine every video clip in the temp folder using FFmpeg concat demuxer
	concat_file = os.path.join(temp_folder_path, 'concat_list.txt')
	with open(concat_file, 'w') as f:
		for clip in clip_files:
			f.write(f"file '{clip}'\n")

	#final_output = os.path.join(temp_folder_path, 'final_output.mp4')

	try:
		concat_command = [
			ffmpeg_path, '-f', 'concat', '-safe', '0', '-i', concat_file, '-c:v', 'libx264', '-c:a', 'aac', '-y',
			output_video
		]
		subprocess.run(concat_command, check=True)
	except subprocess.CalledProcessError as e:
		print(f"Error during video concatenation: {e}")
		return  # Exit the function on failure

	# Cleanup temp files and folder
	for clip in os.listdir(temp_folder_path):
		os.remove(os.path.join(temp_folder_path, clip))
	os.rmdir(temp_folder_path)

	print(f"Video processed and saved to {output_video}")

# ------------------------------------------------------------
gpt = openai_gpt(api_key=config.gpt_key, model=config.gpt_model)

'''
while 1:
	video_path = input("\nVideo Input\n:> ")
	video_path = video_path.replace('\"', '').replace('\'', '')
	if os.path.exists(video_path):
		print(video_path)
		time.sleep(0.5)
		break
'''
video_path = r"D:\GDrive\Temp\footages_prum_mango seasoning\VID_20250220_094709.mp4"

#transcribe_path = os.path.join(os.path.dirname(video_path), os.path.basename(video_path).split('.')[0] + '__transcription.txt')
transcribe_path = os.path.join(os.path.dirname(video_path), 'transcriptions.txt')
if not os.path.exists(transcribe_path):
	pass
	#audio_path = convert_video_to_mp3(video_path)
	#transcribe_convert(audio_path, transcribe_path)
transcribe_convert(video_path, transcribe_path, silen_db=-25, silen_duration=0.4)

1/0

text_script = open(transcribe_path).read()
print('\n'+text_script+'\n')

while 1:
	continue_input = input("Please review all transcription above and please edit...\n{}\n\nDo you want to continue? (yes/no): ".format(transcribe_path))
	if continue_input.lower() in ["yes", "y"]:
		#reload txt path
		text_script = open(transcribe_path).read()
		break

style_ls = ['Friendly', 'Netural', 'Intensive formal', 'Middle-Old English']
while 1:
	style_idx = input("\nSpeaking Style ( Index ) {}\n:> ".format([(i, style_ls[i]) for i in range(len(style_ls))]))
	style_idx = int(style_idx)
	if int(style_idx) in range(len(style_ls)):
		print(style_ls[style_idx], style_idx)
		time.sleep(0.5)
		break

improve_note_path = os.path.join(os.path.dirname(video_path), os.path.basename(video_path).split('.')[0] + '__improve_notes.txt')
sys_prompt = '''
You are an assistant and content creator (script writer plus) that summarizes and guesses what the conversation is presenting about.

Your task step by step: 
1. **Topic** - Provide an interesting topic to attract the audience's paying attention.
2. **Introduction Script** - You are performing as the video blogger and create the guidance talkig script from all summarization.
3. **Suggestion** - Provide your 3 suggestions at least from received content in bullet point text format.

Your format output must be easy to understand for reading, and it should be the system prompt for another response.
'''.strip()
gpt.set_sys_prompt(sys_prompt)
for n in range(config.retry_n):
	completion = gpt.get_completion_response(text_script, temperature=0.25, top_p=0.9)
	if completion:
		break
	else:
		time.sleep(10)
if completion:
	content = completion['choices'][0]['message']['content']
	with open(improve_note_path, 'w') as f:
		f.write(content)
		f.close()
	print(content)
else:
	raise Warning('Connection is failed..')

talking_script_path = os.path.join(os.path.dirname(video_path), os.path.basename(video_path).split('.')[0] + '__talking_script.json')
j_format = '''
{
	"topic" : [fill topic here],
	"introduction" : [Talking script for introduction, interesting, exciting, beginning],
	"details" : [Talking script for the detail, information, fact, consequences, step by step],
	"conclusion" : [Talking script for the conclusion, result, output, summarize, ending]
}
'''
sys_prompt = '''
You are the video content creator who make short reel content writing the talking script from the topic and informations you have got.

Your task is to:
1. Generate talking script for 50 seconds or 1 minutes maximum duration.
2. Create more varity from the transcription to present further and make tone more enthusiasm since in 5 seconds begining.
3. Provide some of detail which are useful for the audience.
4. Write the talking script making {1} and warm tone.
5. Make it simple easy to understand and with no jargon.

**Suggestion & Notes**
{0}

You output or reply must be following these below and fill up in the square brackets from the template as valid JSON
{2}
'''.format(
	open(improve_note_path).read(), style_ls[style_idx], j_format
).strip()
gpt.set_sys_prompt(sys_prompt)
for n in range(config.retry_n):
	completion = gpt.get_completion_response(open(transcribe_path).read(), temperature=0.25, top_p=0.9)
	if completion:
		break
	else:
		time.sleep(10)
if completion:
	content = completion['choices'][0]['message']['content']
	with open(talking_script_path, 'w') as f:
		f.write(content)
		f.close()
	print(content)
else:
	raise Warning('Connection is failed..')

'''
while 1:
	topic_prompt = input("\nWhat is the topic was talking about?\ne.g.\n- Mango plum trees and their growth progress.\n- A step-by-step guide to assembling a solar panel setup\n:> ")
	if topic_prompt != '':
		break
'''

sys_prompt = '''
You are an assistant that refines spoken-word transcriptions into **{2}** language style while ensuring fluent, 
natural English (B1-C2 proficiency). 
Your goal is to improve clarity while preserving the speaker’s intent by acting like them.

Information that you have to know:
**Improval Notes**
{0}

Your task:  
1. Correct grammar, word choice, phrasing, and sentence structure for clarity.  
2. Maintain a conversational, natural tone.  
3. Enhance sentence flow by replacing awkward or unnatural phrasing.  
4. Format the output as valid JSON, with each entry structured as {1}.  
5. Interpret meaning based on the topic, adjusting unclear words or phrases accordingly.  
6. Paraphrase unclear sentences while keeping the main idea and details intact.  
7. Keep timecodes separate when possible but paraphrase short phrases to create smoother sentences.  
8. Expand brief or abrupt statements for better coherence.  
9. Avoid repetition by using synonyms and varied phrasing.  
10. Preserve the speaker’s key points without adding uncertainty or changing intent.  
11. Infer the speaker’s meaning when necessary to maintain logical flow.  
'''.format(
    open(improve_note_path).read(), json.dumps({"HH:MM:SS.MS": "speech generation message"}), style_ls[style_idx]
).strip()
gpt.set_sys_prompt(sys_prompt)
for n in range(config.retry_n):
	completion = gpt.get_completion_response(text_script, temperature=0.25, top_p=0.9)
	if completion:
		break
	else:
		time.sleep(10)

if not completion:
	raise Warning('GPT Connection timeout')

if completion:
	content = completion['choices'][0]['message']['content']
	try:
		json.loads(content)
	except:
		raise Warning(content + '\nJson parser error...\n')
	else:
		new_script_path = util.get_rename_file_extension(transcribe_path, 'json')
		with open(new_script_path, 'w') as f:
			json.dump(json.loads(content), f, indent=4)
			f.close()
	finally:
		pass
		#os.remove(audio_path)
		#os.remove(transcribe_path)

if completion:
	perform_text_burn_in(new_script_path, video_path,
						 os.path.dirname(video_path) + os.sep + os.path.basename(video_path).split('.')[
							 0] + '__guidance.' + os.path.basename(video_path).split('.')[-1])

