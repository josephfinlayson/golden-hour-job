import glob
import os
from datetime import datetime
from subprocess import DEVNULL, STDOUT, run
from time import sleep, time
from pytz import utc

import requests
from picamera import PiCamera
from requests_toolbelt.multipart import encoder
from utils.has_internet import has_internet
from utils.is_golden_hour import is_golden

from utils.video_processing import orchestrate_video_creation


def take_picture(image_name, camera: PiCamera):
    names = []
    evs = [-25,-10,0,10,25]
    for ev in evs:
        name = image_name  + "_slice_" + str(ev).replace('-', "minus_") + ".jpg" 
        camera.exposure_compensation = ev
        sleep(0.5)
        camera.capture(name, resize=(1920, 1080))
        names.append(name)
    sleep(1)
    cmd = ['/usr/bin/enfuse', "-o", image_name +".jpg", *names]
    print("cmd: "+ " ".join(cmd))
    run(cmd, 
    stdout=DEVNULL,
    stderr=STDOUT
    )
    for name in names: 
        os.unlink(name)
    

def delete_files():
    for file in sorted(glob.glob('image*.jpg')):
        os.remove(file)
        
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H:%M:%S")
    os.rename('project.mp4', "golden-hour-videos/" + dt_string + '.mp4' )

def post_to_instagram(file):
    print("posting to instagram")
    with open(file, "rb") as f:
        file_data = [('image', (file, f, 'video/mp4'))]
        response = requests.post("https://golden-hour.josephfinlayson.com/api/image", files=file_data)
        print(response)


def upload_video_queue():
    for file_name in sorted(glob.glob('./videos/final_*.mp4')):
        post_to_instagram(file_name)
        os.remove(file_name)


def filename_generator():
    range = iter(range(1, 10000))
    for n in range:
        yield f'image{n:05}'

def get_video_filename():
    now = datetime.utcnow()
    return f"{now.date()}_{now.hour}:{now.minute}"

def configure_camera():
    camera = PiCamera()
    camera.meter_mode = "backlit"
    camera.saturation = 20
    camera.resolution = (4056, 3040)
    camera.start_preview()
    sleep (5)
    return camera

def app():
    print("starting")
    while True:
        print("checking if golden hour")
        if has_internet():
            print("I haz internet, uploading video queue")
            upload_video_queue()

        if is_golden():
            print("it's golden hour!")
            filenames = []
            camera = configure_camera()
            filename_gen = filename_generator()
            while is_golden():
                filename = next(filename_gen)
                filenames.append(filename)
                take_picture(filename, camera)
                sleep(15)
            orchestrate_video_creation(filenames, "Sunrise/Sunset", filename=get_video_filename())
            camera.stop_preview() 
            camera.close()
            for file in filenames:
                os.unlink(file)

                        
        sleep(240)

if __name__ == "__main__":
   app()