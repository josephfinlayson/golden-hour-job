import requests
from picamera import PiCamera
from time import sleep

camera = PiCamera()

def app():
    print("hello")
    while True:
        is_golden_hour = requests.get("https://golden-hour.hobby-paas.cf/").json()['golden_hour']
        if is_golden_hour: 
            stream = io.BytesIO()
            with picamera.PiCamera() as camera:
                camera.start_preview()
                # Camera warm-up time
                time.sleep(2)
                camera.capture(stream, 'jpeg')
        sleep(5)


if __name__ == "__main__":
    app()
