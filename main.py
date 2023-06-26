import json
import os
import boto3
import logging
from moviepy.editor import concatenate_videoclips, TextClip, ImageClip, CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to convert text to speech
def text_to_speech(text, filename, language):
    # boto3 setup
    session = boto3.Session(profile_name='default', region_name="us-east-1")  # Use your profile name here
    if language == 'jp':
        voice_id = 'Tomoko'
    elif language == 'en':
        voice_id = 'Joanna'
    else:
        raise ValueError(f"Unsupported language: {language}")

    polly_client = session.client('polly')

    response = polly_client.synthesize_speech(
        VoiceId=voice_id,
        OutputFormat='mp3',
        Text=text,
        Engine='neural'
    )

    with open(filename, 'wb') as file:
        file.write(response['AudioStream'].read())

    logging.info(f"Generated audio file: {filename}")


# Function to create text image
def text_to_image(text, filename):
    image = Image.new('RGB', (1080, 720), color=(73, 109, 137))  # Adjust resolution here for 1080p
    d = ImageDraw.Draw(image)
    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 30)  # Adjust this line
    d.text((10, 10), text, font=fnt, fill=(255, 255, 0))
    image.save(filename)


# Create the media directory if it doesn't exist
os.makedirs('media', exist_ok=True)

# Load data from json
with open('5ways.json', 'r') as file:
    data = json.loads(file.read())

clips = []
welcome_clip = TextClip("Welcome", fontsize=70, color="white").set_duration(5)
clips.append(welcome_clip)

bg_image_clip = ImageClip('media/bg_img.png')

# Convert the script to speech for each set of phrases
for key, phrases in data.items():
    for index, phrase in enumerate(phrases, start=1):
        japanese_phrase = phrase.get('japanese')
        english_explanation = phrase.get('explanation')

        text = f"Japanese Phrase: {japanese_phrase}\nExplanation: {english_explanation}"
        jp_filename = f"media/{key}_jp_{index}.mp3"
        en_filename = f"media/{key}_en_{index}.mp3"

        text_to_speech(text, jp_filename, 'jp')
        text_to_speech(text, en_filename, 'en')

        logging.info(f"Generated Japanese audio: {jp_filename}")
        logging.info(f"Generated English audio: {en_filename}")

        audio = AudioFileClip(jp_filename)
        audio_duration = audio.duration

        text_image_filename = f"media/{key}_{index}.png"
        text_to_image(text, text_image_filename)

        image_clip = ImageClip(text_image_filename).set_duration(audio_duration)
        bg_clip = bg_image_clip.set_duration(audio_duration)
        composite_clip = CompositeVideoClip([bg_clip, image_clip])
        composite_clip.duration = audio_duration

        clips.append(composite_clip)

goodbye_clip = TextClip("Goodbye", fontsize=70, color="white").set_duration(5)
clips.append(goodbye_clip)

final_clip = concatenate_videoclips(clips)
final_clip.write_videofile("media/final_output.mp4", fps=24)

logging.info("Video generation completed")
