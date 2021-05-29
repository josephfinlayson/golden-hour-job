from pprint import pprint
from moviepy.video.VideoClip import TextClip
from moviepy.editor import CompositeVideoClip

from moviepy.video.io.VideoFileClip import VideoFileClip
import requests
from datetime import datetime, timedelta
import os 
import cv2
import numpy as np
import glob
from time import sleep
from media import prepare_video


def create_opencv_image_from_stringio(images):
    for image in images:
        with open(image, 'rb') as i:
            i.seek(0)
            image_bytes = i.read()  
            decoded = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
            yield decoded

def orchestrate_video_creation(image_list, text):
    first_image_reference = image_list.pop()

    generator = create_opencv_image_from_stringio([first_image_reference])
    first_image = next(generator)
    height, width, layers = first_image.shape

    size = (width,height)
    print("resolution of images", size)
    video_path = 'project.mp4'
    frames_per_second = len(image_list) / 12
    print("frames per second", frames_per_second)
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), frames_per_second, size)

    for img in create_opencv_image_from_stringio(image_list):
        out.write(img)

    out.release()
    
    sleep(1)

    prepare_video(video_path,   aspect_ratios=(9/16), max_duration=14.9, 
            min_size=(612, 612), max_size=(1080, 1920), save_path='second.mp4')

    # TODO: set text a bit up from bottom
    text = TextClip(text,fontsize=54, color='blue').set_position(("center")).set_duration(4)
    clip = VideoFileClip('second.mp4', audio=False)
    final_clip = CompositeVideoClip([clip, text])
    final_clip.write_videofile(video_path, fps=frames_per_second )
    text.close()    
    clip.close()
    final_clip.close()
    return {'file': 'project.mp4'}        