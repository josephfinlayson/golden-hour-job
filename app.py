import glob
import io
import os
import subprocess
from datetime import datetime
from subprocess import DEVNULL, STDOUT, run
from time import sleep, time

import requests
from picamera import PiCamera
from requests_toolbelt.multipart import encoder

from video_processing import orchestrate_video_creation


def take(image_name, camera: PiCamera):
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
    

def is_golden_hour():
    return requests.get("https://golden-hour.josephfinlayson.com/").json()['golden_hour']

def get_image_list():
    print("Creating video")
    img_array = []
    for file in sorted(glob.glob('image*.jpg')):
        img_array.append(file)
    return img_array

def delete_files():
    for file in sorted(glob.glob('image*.jpg')):
        os.remove(file)
        
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H:%M:%S")
    os.rename('project.mp4', "golden-hour-videos/" + dt_string + '.mp4' )

def post_to_instagram():
    print("posting to instagram")
    with open("project.mp4", "rb") as f:
        file_data = [('image', ('project.mp4', f, 'video/mp4'))]
        response = requests.post("https://golden-hour.josephfinlayson.com/api/image", files=file_data)
        print(response)

def render_and_post(camera):
    imgs = get_image_list()
    orchestrate_video_creation(imgs, "Sunrise/Sunset")
    post_to_instagram()
    delete_files()
    camera.stop_preview() 
    camera.close()


def filename_generator():
    r = iter(range(1, 10000))
    for n in r:
        yield f'image{n:05}'


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
        if is_golden_hour():
            print("it's golden hour!")
            camera = configure_camera()
            t_end = time() + 60 * 80
            fn_gen = filename_generator()
            while time() < t_end:
                filename = next(fn_gen)
                print(filename)
                take(filename, camera)
                sleep(15)
            
            render_and_post(camera)
                        
        sleep(240)

if __name__ == "__main__":
   app()
#   render_and_post(PiCamera())


# camera.framerate = 30
# Wait for the automatic gain control to settle
# Now fix the values
# camera.shutter_speed = camera.exposure_speed
# camera.exposure_mode = 'off'
# g = camera.awb_gains
# camera.awb_mode = 'off'
# camera.awb_gains = g
