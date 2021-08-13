import streamlit as st
import shutil
import cv2
import os
from os import path
import numpy as np
import noisereduce as nr
import scipy
from scipy.io import wavfile

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import make_chunks
import glob

from googletrans import Translator
translator = Translator()

st.title("Extract text from video")
try:
    os.mkdir("temp")
except:
    pass
for i in os.listdir("./temp/"):
    try:
        os.remove(os.remove(f"./temp/{i}"))
    except:
        pass
input_file_path = ""
uploaded_file = st.file_uploader("Upload Files", type=["mp4"])
if uploaded_file is not None:
    with open(f"./temp/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    input_file_path = f"./temp/{uploaded_file.name}"

noise_remove_button = st.checkbox("Remove Audio Noise")
flip = st.checkbox("Mirror Video")
    

# folder_path = st.text_input("Paste the folder location where you want to save:")
# flag = path.exists(folder_path)
flag=True
in_lang = st.selectbox(
    "Select your input language",
    ("English", "Hindi", "Bengali", "korean", "Chinese", "Japanese","Spanish"),
)
if in_lang == "English":
    input_language = "en"
elif in_lang == "Hindi":
    input_language = "hi"
elif in_lang == "Bengali":
    input_language = "bn"
elif in_lang == "korean":
    input_language = "ko"
elif in_lang == "Chinese":
    input_language = "zh-cn"
elif in_lang == "Japanese":
    input_language = "ja"
elif in_lang == "Spanish":
    input_language = "es"

out_lang = st.selectbox(
    "Select your output language",
    ("English", "Hindi", "Bengali", "korean", "Chinese", "Japanese","Spanish"),
)
if out_lang == "English":
    output_language = "en"
elif out_lang == "Hindi":
    output_language = "hi"
elif out_lang == "Bengali":
    output_language = "bn"
elif out_lang == "korean":
    output_language = "ko"
elif out_lang == "Chinese":
    output_language = "zh-cn"
elif out_lang == "Japanese":
    output_language = "ja"
elif out_lang == "Spanish":
    output_language = "es"
     

english_accent = st.selectbox(
    "Select your english accent",
    (
        "Default",
        "India",
        "United Kingdom",
        "United States",
        "Canada",
        "Australia",
        "Ireland",
        "South Africa",
        "Spanish"
    ),
)

if english_accent == "Default":
    tld = "com"
elif english_accent == "India":
    tld = "co.in"

elif english_accent == "United Kingdom":
    tld = "co.uk"
elif english_accent == "United States":
    tld = "com"
elif english_accent == "Canada":
    tld = "ca"
elif english_accent == "Australia":
    tld = "com.au"
elif english_accent == "Ireland":
    tld = "ie"
elif english_accent == "South Africa":
    tld = "co.za"
elif english_accent == "Spanish":
    tld = "com.mx"


def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:10]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text


display_output_text = st.checkbox("Display output text")


   







if st.button("Start"):
    if flip:
        var2 = os.system(f'ffmpeg -i {input_file_path} -vf hflip -c:a copy "./temp/flip_{uploaded_file.name}')
        input_file_path=f'./temp/flip_{uploaded_file.name}'
    if flag:
        var1 = os.system(f'ffmpeg -i {input_file_path} "./temp/audio.wav"')
        if var1 == 0:
            print("audio extracted")
            audio_file_path="./temp/audio.wav"
            if noise_remove_button:
                rate, data = wavfile.read("./temp/audio.wav")
                reduced_noise = nr.reduce_noise(y=data, sr=rate)
                scipy.io.wavfile.write("./temp/noise_free.wav",rate,reduced_noise)
                audio_file_path="./temp/noise_free.wav"
            audio = AudioSegment.from_file(audio_file_path)
            duartion=audio.duration_seconds
            vocal_file=audio_file_path
            if int(duartion)>20:
                myaudio = AudioSegment.from_file(audio_file_path , "wav") 
                chunk_length_ms = 20000 
                chunks = make_chunks(myaudio, chunk_length_ms) 

                for i, chunk in enumerate(chunks):
                    chunk_name = "./temp/{0}.wav".format(i)
                    print("exporting", chunk_name)
                    chunk.export(chunk_name, format="wav")
                filess = []
                for filename in glob.glob("./temp/*wav"):
                    filess.append(filename)
                try:
                    filess.remove(audio_file_path)
                except:
                    try:
                        filess.remove('./temp\\audio.wav')
                    except:
                        pass
                try:
                    filess.remove(audio_file_path)
                except:
                    try:
                        filess.remove('./temp\\noise_free.wav')
                    except:
                        pass
                filess.sort()
                print(filess)
            if int(duartion)<20:
                filess=[audio_file_path]
                print(filess)
            long_text=""
            r = sr.Recognizer()
            for i in filess:
                print(f"Scanning {i}")
                with sr.AudioFile(i) as source:
                    r.adjust_for_ambient_noise(source)
                    audio_listened = r.listen(source)
                try:
                    text = r.recognize_google(audio_listened,language=in_lang)
                    long_text+=text+" "
                except sr.UnknownValueError:
                    print("can't scan :" +i+" empty or file_size big")
                    continue 
            text=long_text
            st.markdown(f"{text}")
            
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## Your audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown(f"## Output text:")
                st.write(f" {output_text}")

            


