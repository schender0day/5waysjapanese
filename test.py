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


def text_to_speech(text, filename, language):
    session = boto3.Session(profile_name='default', region_name="us-east-1")
    voice_id = 'Tomoko' if language == 'jp' else 'Stephen'
    polly_client = session.client('polly')
    response = polly_client.synthesize_speech(VoiceId=voice_id, OutputFormat='mp3', Text=text, TextType='text',
                                              Engine='neural')
    with open(filename, 'wb') as file:
        file.write(response['AudioStream'].read())
    logging.info(f"Generated audio file: {filename}")


def create_text_clip(phrase, fontsize, font, color, duration, position):
    return (
        TextClip(phrase, fontsize=fontsize, font=font, color=color, method='caption', align='center', size=(1080, 1920))
        .set_duration(duration)
        .set_position(position))


def get_font_by_platform():
    if platform.system() == 'Windows':
        return 'MS Gothic'
    else:
        return 'Osaka'


os.makedirs('media', exist_ok=True)

with open('5ways.json', 'r') as file:
    data = json.load(file)
data_keys = list(data.keys())
key = data_keys[0]
values = data[key]
bg_video = VideoFileClip("media/916_bg.mp4")
for video_index, phrase in enumerate(values, start=1):
    start_time = time.time()

    video_clips = []
    audio_clips = []
    silence = AudioArrayClip(np.array([[0] * 44100] * 2).T, fps=44100)

    welcome_filename = f"media/welcome_{video_index}.mp3"
    text_to_speech(f"Let's talk 7 ways to say {key} in Japanese.", welcome_filename, 'en')
    welcome_audio = AudioFileClip(welcome_filename).fx(afx.audio_normalize)
    thumbnail_video = VideoFileClip("media/916_thumbnail.mp4").subclip(0, 5)
    thumbnail_video = thumbnail_video.set_duration(5).set_audio(welcome_audio)

    # Create video index text clip
    index_text_clip = create_text_clip(f"Episode {video_index}/7", 36, 'media/Gliker-Black.ttf', 'dark red', thumbnail_video.duration,
                                       ('center', -900))
    welcome_video = CompositeVideoClip([thumbnail_video, index_text_clip])

    audio_clips.append(welcome_audio)
    audio_clips.append(silence.set_duration(2))
    video_clips.append(welcome_video)

    jp_filename = f"media/jp_{video_index}.mp3"
    en_filename = f"media/en_{video_index}.mp3"
    text_to_speech(phrase['japanese'], jp_filename, 'jp')
    text_to_speech(phrase['explanation'], en_filename, 'en')
    logging.info(f"Generated audio file: {jp_filename}")
    logging.info(f"Generated audio file: {en_filename}")
    # Load and normalize audio
    jp_audio = AudioFileClip(jp_filename).fx(afx.audio_normalize)
    en_audio = AudioFileClip(en_filename).fx(afx.audio_normalize)


    # Repeat Japanese audio 3 times
    jp_audio_repeated = concatenate_audioclips([jp_audio, silence, silence,jp_audio, silence, silence, jp_audio])

    # Add Japanese and English audio to audio_clips
    audio_clips.append(jp_audio_repeated)
    en_audio = concatenate_audioclips([silence, en_audio])
    audio_clips.append(en_audio)

    # Generate video with text overlays
    # modified to match the duration of jp_audio_repeated and en_audio

    full_video = bg_video.subclip(0, jp_audio_repeated.duration + en_audio.duration)
    index_text_clip = create_text_clip(f"Episode {video_index}/7", 36, 'media/Gliker-Black.ttf', 'dark red',
                                       full_video.duration,
                                       ('center', -900))
    full_video = CompositeVideoClip([full_video, index_text_clip])
    font_size = 75  # Define the size of text
    head_size = 85  # Define the size of the header
    en_head_size = 80

    line_height = 30  # Define the height of line
    margin = -350

    # Generate video with text overlays
    # modified to match the duration of jp_audio_repeated and en_audio
    full_video = bg_video.subclip(0, jp_audio_repeated.duration + en_audio.duration)
    # Create video index text clip for full_video
    index_text_clip_full = create_text_clip(f"Episode {video_index}/7", 36, 'media/Gliker-Black.ttf', 'dark red', full_video.duration,
                                            ('center', -900))
    full_video = CompositeVideoClip([full_video, index_text_clip_full])
    # Positions for the text
    y_position_jp = margin
    y_position_en = y_position_jp + font_size + line_height  # place English text below Japanese text
    y_position_explanation = y_position_en + font_size + line_height + 400

    # Create TextClips with the helper function
    jp_text_clip = create_text_clip(phrase['japanese'], head_size, get_font_by_platform(), 'dark red',
                                    jp_audio_repeated.duration + en_audio.duration, ('center', y_position_jp))
    en_text_clip = create_text_clip(phrase['english'], head_size, get_font_by_platform(), 'black',
                                    jp_audio_repeated.duration + en_audio.duration, ('center', y_position_en))
    explanation_text_clip = create_text_clip(phrase['explanation'], font_size, get_font_by_platform(), 'black',
                                             jp_audio_repeated.duration + en_audio.duration,
                                             ('center', y_position_explanation))

    # Create a composite video clip that includes the video and all text clips
    # Set the duration of the composite video clip to the total duration of the audio clips
    combined_clip = CompositeVideoClip(
        [full_video, jp_text_clip, en_text_clip, explanation_text_clip]).set_duration(
        jp_audio_repeated.duration + en_audio.duration)

    # # Add combined clip to video_clips
    video_clips.append(combined_clip)
    ending_video = VideoFileClip("media/916_ending.mp4").subclip(0, 8)
    video_clips.append(ending_video)
    # video_clips.append(combined_clip)
    # ending_video = VideoFileClip("media/916_ending.mp4").subclip(0, 5)
    # video_clips.append(ending_video)
    text_to_speech("Thanks for watching Explore my channel for more videos in this series and full videos with examples.", "media/ending.mp3", 'en')
    ending_audio = AudioFileClip("media/ending.mp3").fx(afx.audio_normalize)
    audio_clips.append(ending_audio)

    audio_clips.append(silence.set_duration(1))

    # # Concatenate all audio and video clips
    final_audio_clip = concatenate_audioclips(audio_clips)
    final_video_clip = concatenate_videoclips(video_clips)
    # final_audio_clip = concatenate_audioclips(audio_clips)
    # final_video_clip = concatenate_videoclips(video_clips)
    #
    # # Trim final_audio_clip to match final_video_clip
    final_audio_clip = final_audio_clip.subclip(0, final_video_clip.duration)
    # final_audio_clip = final_audio_clip.subclip(0, final_video_clip.duration)
    #
    # # Attach audio to video
    final_video = final_video_clip.set_audio(final_audio_clip)
    # final_video = final_video_clip.set_audio(final_audio_clip)
    #
    # # Write final video to file
    final_video.write_videofile(f"media/video_{video_index}.mp4", codec='libx264')
    # final_video.write_videofile("media/final_video_1.mp4", codec='libx264')
    #
    # # Add timer end right after the video creation process
    end_time = time.time()
    execution_time = end_time - start_time

    print("Video generated successfully!")
    print("Execution time:", execution_time, "seconds")
    print("Video generated successfully!")
