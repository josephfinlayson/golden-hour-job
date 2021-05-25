import requests
from picamera import PiCamera
from time import sleep
import io
import glob
import os
from datetime import datetime
from requests_toolbelt.multipart import encoder
from video_processing import orchestrate_video_creation


def is_golden_hour():
    return requests.get("https://golden-hour.hobby-paas.cf/").json()['golden_hour']

def images_to_bytes():
    print("Creating video")
    img_array = []
    for file in sorted(glob.glob('*.jpg')):
        image = open(file, 'rb')
        img_array.append(image)
    return img_array

def delete_files():
    for file in sorted(glob.glob('*.jpg')):
        os.remove(file)
        
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H:%M:%S")
    os.rename('project.mp4', "golden-hour-videos/" + dt_string + '.mp4' )

def post_to_instagram():
    print("posting to instagram")
    with open("project.mp4", "rb") as f:
        file_data = [('image', ('project.mp4', f, 'video/mp4'))]
        response = requests.post("https://golden-hour.hobby-paas.cf/api/image", files=file_data)
        print(response)

def render_and_post(camera):
    imgs = images_to_bytes()
    orchestrate_video_creation(imgs, "Sunrise/Sunset")
    post_to_instagram()
    delete_files()
    camera.stop_preview() 
    camera.close()

def app():
    print("starting")
    while True:
        print("checking if golden hour")
        if is_golden_hour(): 
            print("it's golden hour!")
            camera = PiCamera()
            camera.rotation = -90
            camera.resolution = (4056, 3040)
            camera.start_preview()
            sleep(2)
            try:
                for filename in camera.capture_continuous('image{counter:03d}.jpg'):
                    print(filename)
                    sleep(15)
                    if not is_golden_hour():
                        break
            finally:
                render_and_post(camera)
                    
        sleep(60)

if __name__ == "__main__":
    app()
 #  render_and_post(PiCamera())
