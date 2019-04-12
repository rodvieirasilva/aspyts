from PIL import Image, ImageDraw
import pystray
import time
from threading import Thread
import sys, signal
from interrupt import GracefulInterruptHandler

def create_image():
    return Image.open("icon.png")

def on_clicked():
    pass

def evento(*args):
    print("Evento disparado")    

def exit_action(icon):
    interrup.interrupted = True
    icon.visible = False
    icon.stop()    

def threaded_function(arg):
    for i in range(arg):
        time.sleep(1)

interrup = None
def callback(icon):
    image = Image.new('RGBA', (128,128), (255,255,255,255)) # create new image
    percent = 100
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()
    while not interrup.interrupted:
        if thread.isAlive():
            step = 5
        else:
            step = 0
            percent = 100
                        
        img = image.copy()
        d = ImageDraw.Draw(img)
        d.rectangle([0, 128, 128, 128-(percent * 128) / 100], fill='blue')
        icon.icon = img
        time.sleep(1)
        percent -= step
        if percent < 0:
            percent = 100
    
    if thread.isAlive():
        thread.join()
    exit_action(icon)
    


#     return image
icon = pystray.Icon(                    \
    'Antoher Python Task Scheduler',    \
    create_image(),                     \
    menu = pystray.Menu(                          \
            pystray.MenuItem(                   \
                'Teste',                \
                on_clicked,            \
                #checked=lambda item: state
                ),                       \
            pystray.MenuItem(                   \
                'Exit',                \
                exit_action,            \
                #checked=lambda item: state
                )                       \
        )                               \
    )

with GracefulInterruptHandler() as i:
    interrup = i
    icon.title = 'Antoher Python Task Scheduler'
    icon.visible = True    
    icon.run(setup=callback)