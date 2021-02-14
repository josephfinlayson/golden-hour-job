import requests
from picamera import PiCamera
from time import sleep
import io
import glob
import os
from datetime import datetime
from requests_toolbelt.multipart import encoder

def is_golden_hour():
    return requests.get("https://golden-hour.hobby-paas.cf/").json()['golden_hour']

def process_video(images):
    print("sending")

    file_data = [('image', ('long.jpg', image, 'applcation/octet-stream')) for image in images]
    file_data.append(('text', "blah"))
    form = encoder.MultipartEncoder(file_data)
    headers = {"Prefer": "respond-async", "Content-Type": form.content_type}
    response = requests.post("https://golden-hour.hobby-paas.cf/post-story", headers=headers, data=form)

    response.raise_for_status()
    with open("project.mp4", "wb") as f:
        f.write(response.content)

def create_video():
    print("Creating video")
    img_array = []
    for file in sorted(glob.glob('*.jpg')):
        image = open(file, 'rb')
        img_array.append(image)
    process_video(img_array)

def delete_files():

    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H:%M:%S")

    os.rename('project.mp4', dt_string + '.mp4' )

    for file in sorted(glob.glob('*.jpg')):
        os.remove(file)

def post_to_instagram():
    print("posting to instagram")
    with open("project.mp4", "rb") as f:
        file_data = [('image', ('project.mp4', f, 'video/mp4'))]
        response = requests.post("https://golden-hour.hobby-paas.cf/api/image", files=file_data)
        print(response)

def app():
    print("starting")
    while True:
        print("checking if golden hour")
        if is_golden_hour(): 
            camera = PiCamera()
            camera.resolution = (2592, 1944)
            camera.rotation = -90
            camera.start_preview()
            sleep(2)
            for filename in camera.capture_continuous('img{counter:03d}.jpg'):
                print("capturing", filename)
                if not is_golden_hour():
                    sleep(5) 
                    create_video()
                    post_to_instagram()
                    delete_files()
                    camera.close()
                    break
                sleep(150)
        sleep(60)

if __name__ == "__main__":
    app()