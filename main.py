# Import necessary libraries
import json
import os
import time
import boto3
import logging
import numpy as np
import platform
from moviepy.audio.AudioClip import concatenate_audioclips, AudioArrayClip
from moviepy.editor import TextClip, afx
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# Video resolution presets
p720 = (1280, 720)
p1080 = (1920, 1080)
p4k = (3840, 2160)
pshort = (1080, 1920)
pshort_single = (1080, 1920)

def get_resolution():
    while True:
        print("Choose the video resolution:\n1: 720p\n2: 1080p\n3: 4K\n4: TikTok Short\n5: TikTok Short (Individual Videos)")
        choice = input("Enter the number of your choice: ")
        logging.debug(f"User selected option: {choice}")
        if choice == '1':
            return p720
        elif choice == '2':
            return p1080
        elif choice == '3':
            return p4k
        elif choice == '4':
            return pshort
        else:
            logging.warning("Invalid choice. User will be prompted again.")
            print("Invalid choice. Please try again.")



# Function to convert text to speech using AWS Polly
def text_to_speech(text, filename, language):
    session = boto3.Session(profile_name='default', region_name="us-east-1")
    voice_id = 'Takumi' if language == 'jp' else 'Stephen'
    polly_client = session.client('polly')
    response = polly_client.synthesize_speech(VoiceId=voice_id, OutputFormat='mp3', Text=text, TextType='text', Engine='neural')
    with open(filename, 'wb') as file:
        file.write(response['AudioStream'].read())
    logging.info(f"Generated audio file: {filename}")

# Function to add text overlays to video
def add_text_to_video(video, text, fontsize=24, font='Arial', pos='center', color='black', resolution=(1280, 720)):
    size = resolution
    text_clip = TextClip(text, fontsize=fontsize, font=font, method='caption', align='center', color=color, size=size)
    text_clip = text_clip.set_duration(video.duration).set_position(pos)
    video = CompositeVideoClip([video, text_clip])
    return video

# Function to get the appropriate font based on platform
def get_font_by_platform():
    if platform.system() == 'Windows':
        return 'MS Gothic'
    else:
        return 'Osaka'

# Function to create a text clip
def create_text_clip(phrase, fontsize, font, color, duration, position):
    return (TextClip(phrase, fontsize=fontsize, font=font, color=color, method='caption', align='center', size=resolution)
            .set_duration(duration)
            .set_position(position))

# Create media directory if it doesn't exist
os.makedirs('media', exist_ok=True)
def hex_to_rgb(hex):
    h = hex.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# Get user-selected resolution
resolution = get_resolution()
# ...
# In your code:
# Add timer start right before the video creation process
# check if user selected resolution is pshort-single
# if yes, then call generate_video() for each phrase in the list
# else, run the original code to generate the video
with open('5ways.json', 'r') as file:
    data = json.load(file)
key = list(data.keys())[0]


start_time = time.time()


# Load data from json


# Initialize clips
audio_clips = []
video_clips = []

# Define silence audio clip
silence = AudioArrayClip(np.array([[0]*44100]*2).T, fps=44100)

# Generate welcome audio and video
welcome_filename = "media/welcome.mp3"
key = list(data.keys())[0]
text_to_speech(f"Welcome, let's talk about 5 ways to say {key} in Japanese", welcome_filename, 'en')
welcome_audio = AudioFileClip(welcome_filename).fx(afx.audio_normalize)
if resolution == pshort:
    thumbnail_video = VideoFileClip("media/916_thumbnail.mp4").subclip(0, 5)
    thumbnail_video = add_text_to_video(thumbnail_video, f"{key}", font="media/AlegreyaSans-Black.ttf", fontsize=200, color="dark red",pos=("center",-200), resolution=resolution)
elif resolution == p1080 or resolution == p4k or resolution == p720:
    thumbnail_video = VideoFileClip("media/169_thumbnail.mp4")
    thumbnail_video = add_text_to_video(thumbnail_video, f"{key}", font="media/Changa-SemiBold.ttf", fontsize=110, pos=(750,50), resolution=resolution)

welcome_video = thumbnail_video.set_duration(5).set_audio(welcome_audio)

# Add welcome audio and video to clips

video_clips.append(welcome_video)
audio_clips.append(welcome_audio)
audio_clips.append(silence.set_duration(1))

# Load background video
if resolution == pshort:
    bg_video = VideoFileClip("media/916_bg.mp4")
elif resolution == p1080 or resolution == p4k or resolution == p720:
    bg_video = VideoFileClip("media/169_bg.mp4")

# Get platform appropriate font
jp_font = get_font_by_platform()
# Iterate over each phrase in the data
# Iterate over each phrase in the data
for index, phrase in enumerate(data[key], start=1):
    # Generate Japanese and English audio
    jp_filename = f"media/jp_{index}.mp3"
    en_filename = f"media/en_{index}.mp3"
    text_to_speech(phrase['japanese'], jp_filename, 'jp')
    text_to_speech(f"{phrase['explanation']}", en_filename, 'en')
    logging.info(f"Generated Japanese audio: {jp_filename}")
    logging.info(f"Generated English audio: {en_filename}")

    # Load and normalize audio
    jp_audio = AudioFileClip(jp_filename).fx(afx.audio_normalize)
    en_audio = AudioFileClip(en_filename).fx(afx.audio_normalize)

    # Repeat Japanese audio 3 times
    jp_audio_repeated = concatenate_audioclips([jp_audio, silence, silence,jp_audio, silence,silence])

    # Add Japanese and English audio to audio_clips
    audio_clips.append(jp_audio_repeated)
    en_audio = concatenate_audioclips([silence, en_audio, silence, silence])
    audio_clips.append(en_audio)

    # Generate video with text overlays
    # modified to match the duration of jp_audio_repeated and en_audio
    full_video = bg_video.subclip(0, jp_audio_repeated.duration + en_audio.duration)

    # Iterate over each phrase in the data
    # for index, phrase in enumerate(data[key], start=1):
        # Other parts of the code...

    if resolution == pshort:
        font_size = 75  # Define the size of text
        head_size = 85  # Define the size of the header
        en_head_size = 80
    elif resolution == p1080 or resolution == p4k or resolution == p720:
        font_size = 50  # Define the size of text
        head_size = 65  # Define the size of the header
        en_head_size = 55

    line_height = 30  # Define the height of line
    margin = -350 if resolution == pshort else 0

    # Generate video with text overlays
    # modified to match the duration of jp_audio_repeated and en_audio
    full_video = bg_video.subclip(0, jp_audio_repeated.duration + en_audio.duration)

    # Positions for the text
    y_position_jp = margin
    y_position_en = y_position_jp + font_size + line_height  # place English text below Japanese text
    y_position_explanation = y_position_en + font_size + line_height + 400 if resolution == pshort else y_position_en + font_size + line_height + 200

    # Create TextClips with the helper function
    jp_text_clip = create_text_clip(phrase['japanese'], head_size, jp_font, 'dark red',
                                    jp_audio_repeated.duration + en_audio.duration, ('center', y_position_jp))
    en_text_clip = create_text_clip(phrase['english'], head_size, jp_font, 'black',
                                    jp_audio_repeated.duration + en_audio.duration, ('center', y_position_en))
    explanation_text_clip = create_text_clip(phrase['explanation'], font_size, jp_font, 'black',
                                             jp_audio_repeated.duration + en_audio.duration,
                                             ('center', y_position_explanation))

    # Create a composite video clip that includes the video and all text clips
    # Set the duration of the composite video clip to the total duration of the audio clips
    combined_clip = CompositeVideoClip(
        [full_video, jp_text_clip, en_text_clip, explanation_text_clip]).set_duration(
        jp_audio_repeated.duration + en_audio.duration)

    # Add combined clip to video_clips
    video_clips.append(combined_clip)

# Add ending video to video_clips
if resolution == pshort:
    ending_video = VideoFileClip("media/916_ending.mp4")
elif resolution == p1080 or resolution == p4k or resolution == p720:
    ending_video = VideoFileClip("media/169_ending.mp4")
video_clips.append(ending_video)

# Concatenate all audio and video clips
final_audio_clip = concatenate_audioclips(audio_clips)
final_video_clip = concatenate_videoclips(video_clips)

# Trim final_audio_clip to match final_video_clip
final_audio_clip = final_audio_clip.subclip(0, final_video_clip.duration)

# Attach audio to video
final_video = final_video_clip.set_audio(final_audio_clip)

# Write final video to file
final_video.write_videofile("media/final_video_1.mp4", codec='libx264')

# Add timer end right after the video creation process
end_time = time.time()
execution_time = end_time - start_time

print("Video generated successfully!")
print("Execution time:", execution_time, "seconds")
print("Video generated successfully!")
