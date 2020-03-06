from jam_picamera import JamPiCamera
from text import get_text
from gpiozero import Button
from twython import Twython
from time import sleep
import logging
import os
from time import gmtime, strftime
from config import folder_id

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import qrcode

logger = logging.getLogger('photobooth')
logging.basicConfig(level=logging.INFO)
logger.info("starting")

text = get_text(language='en')

camera = JamPiCamera()
button = Button(14, hold_time=5)

camera.resolution = (1024, 768)
camera.start_preview()
camera.annotate_text_size = 70

google = True


def google_auth():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    return drive


if google:
    drive = google_auth()


def quit():
    logger.info("quitting")
    camera.close()


def countdown(n):
    logger.info("running countdown")
    for i in reversed(range(n)):
        camera.annotate_text = '{}...'.format(i + 1)
        sleep(1)
    camera.annotate_text = None


def capture_photos(n):
    """
    Capture n photos in sequence and return a list of file paths
    """
    photos = []

    folder_name = strftime("/home/pi/Pictures/photo-%d-%m %H:%M:%S", gmtime())

    os.mkdir(folder_name)

    for pic in range(n):
        camera.annotate_text = text['photo number'].format(pic + 1, n)
        sleep(1)
        camera.annotate_text = text['press to capture']
        button.wait_for_press()
        logger.info("button pressed")
        button.wait_for_release()
        logger.info("button released")
        sleep(1)
        countdown(3)
        logger.info("capturing photo")
        picture_path = folder_name + '/image' + str(pic) + '.png'
        camera.capture(picture_path)
        logger.info("captured photo: {}".format(pic))
        photos.append(picture_path)
    return photos


def display_qr(link):
    img = qrcode.make(link)
    img.save('qr.png')


def upload_photos(photos):
    folder_name = photos[0].split('/')[:-1]

    folder = drive.CreateFile({'title': folder_name,
                               "parents": [{"id": folder_id}],
                               "mimeType": "application/vnd.google-apps.folder"})
    folder.Upload()

    for image in photos:
        file = drive.CreateFile({'parents': [{'id': folder['id']}],
                                 'title': image})
        file.SetContentFile(folder_name+'/'+image)
        file.Upload()

    link = folder['alternateLink']

    return link


button.when_held = quit

while True:
    camera.annotate_text = text['ready']
    logger.info("waiting for button press")
    button.wait_for_press()
    logger.info("button pressed")
    photos = capture_photos(4)

    if google:
        logger.info("google upload enabled")
        camera.annotate_text = text['uploading to Drive with cancel']
        pressed = button.wait_for_press(timeout=3)
        if pressed:
            logger.info("button pressed - not uploading")
            camera.annotate_text = text['not uploading to Drive']
            button.wait_for_release()
            sleep(2)
        else:
            logger.info("button not pressed - tweeting")
            camera.annotate_text = text['uploading']
            try:
                link = upload_photos(photos)

                display_qr(link)

                sleep(1)
            except:
                logger.info("failed to upload")
                camera.annotate_text = text['failed upload']
                sleep(2)
