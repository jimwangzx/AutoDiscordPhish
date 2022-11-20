import pyautogui
import time
import requests
import pytesseract
import os
from random import randint
from dotenv import load_dotenv

delay_between_clicks = 2.2
delay_bewteen_img_check = 0.1
precision = 0.9
max_retry = 3
button_file = 'assets/img/button.png'
url_webhook = os.getenv('URL_WEBHOOK')
discord_id = os.getenv('DISCORD_ID')
captcha_file = 'assets/img/screen-captcha.png'
current_captcha_file = 'assets/img/current_captcha.png'

def getCaptchaText():
    # Set a screnshot of the captcha
    img_captcha = pyautogui.screenshot(region=(0, 0, 1920, 1080))
    img_captcha.save(current_captcha_file)
    # Return the text from the captcha picture
    text = pytesseract.image_to_string(current_captcha_file)
    text = text.split('with this captcha.')[1]
    text = text.split('Note: ')[0]
    text = text.replace(' ', '').replace('\n', '').replace('\x0c', '')
    return text

def sendCaptcha(verification_code):
    pyautogui.write('/verify ' + verification_code, interval=0.25)
    pyautogui.press('enter')
    print('Captcha sent')
    sendFish()

def solveCaptcha():
    verification_code = getCaptchaText()
    # Sleep a random time to avoid detection of automatic captcha resolution
    time.sleep(randint(10, 15))
    if len(verification_code) == 6:
        sendCaptcha(verification_code)
    else:
        notifyDiscord()
        print('Captcha not solved, stopping')
        print('Captcha text: ' + verification_code)
        
        button = pyautogui.locateOnScreen(image, confidence=precision, grayscale=True, region=(0, 0, 1920, 1080))
        while button is None:
            time.sleep(30)
            button = pyautogui.locateOnScreen(image, confidence=precision, grayscale=True, region=(0, 0, 1920, 1080))
        
        print('Button found, restarting')
        sendFish()

def checkCaptcha():
    img_captcha = pyautogui.locateOnScreen(captcha_file, confidence=precision, grayscale=True, region=(0, 0, 1920, 1080))
    if img_captcha is not None:
        print('Captcha found, stopping')
        solveCaptcha()

def sendFish():
    pyautogui.press('/fish', interval=0.25)
    pyautogui.press('enter')

def notifyDiscord():
    url = url_webhook
    data = {
        'content': '<@'+ discord_id +'> the bot is stuck, please check it'
    }
    requests.post(url, json=data)

def getImagePosition(image):
    button = pyautogui.locateOnScreen(image, confidence=precision, grayscale=True, region=(0, 0, 1920, 1080))
    x = 0
    while button is None:
        print('Button not found')
        time.sleep(delay_bewteen_img_check)
        button = pyautogui.locateOnScreen(image, confidence=precision, grayscale=True, region=(0, 0, 1920, 1080))
        sendFish()
        x += 1
        if x > max_retry:
            # call webhook discord
            notifyDiscord()
            print('Button not found, stopping')
            exit()
    return button

def click(image):
    button = getImagePosition(image)
    button_x, button_y = pyautogui.center(button)
    pyautogui.click(button_x, button_y)
    time.sleep(delay_between_clicks)

delay_between_clicks += 0.3
while True:
    click(button_file)
    checkCaptcha()
