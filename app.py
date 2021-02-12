import requests
from picamera import PiCamera
from time import sleep
import io
import glob
import os

def is_golden_hour():
    return requests.get("https://golden-hour.hobby-paas.cf/").json()['golden_hour']

def process_video(images):
    print("sending images")
    file_data = [('image', ('long.jpg', image, 'image/jpeg')) for image in images]
    response = requests.post("https://golden-hour.hobby-paas.cf/post-story", files=file_data, data=dict(text="Garden"))
    print(response)
    response.raise_for_status()
    with open("project.mp4", "wb") as f:
        f.write(response.content)

def create_video():
    img_array = []
    for file in sorted(glob.glob('*.jpg')):
        image = open(file, 'rb')
        image.seek(0)
        img_array.append(image)
    process_video(img_array)

def delete_files():
    for file in sorted(glob.glob('*.jpg')):
        os.remove(file)

def post_to_instagram():
    with open("project.mp4", "rb") as f:
        file_data = [('image', ('project.mp4', f, 'video/mp4'))]
        response = requests.post("https://golden-hour.hobby-paas.cf/api/image", files=file_data)
        print(response)

def app():
    while True:
        print("checking if golden hour")
        if is_golden_hour(): 
            camera = PiCamera()
            camera.resolution = (2592, 1944)
            camera.rotation = -90
            for filename in camera.capture_continuous('img{counter:03d}.jpg'):
                print('Captured %s' % filename)
                if not is_golden_hour():
                    sleep(5) 
                    create_video()
                    post_to_instagram()
                    delete_files()
                    camera.close()
                sleep(300)
        sleep(60)

if __name__ == "__main__":
    app()
