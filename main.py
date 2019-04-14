from PIL import Image, ImageDraw
import pystray
import time
from db import DB
from threading import Thread
import sys, signal
from interrupt import GracefulInterruptHandler
import glob
from os import path
import subprocess

def create_image():
    return Image.open("icon.png")

def on_clicked(id_task):
    def inner(icon, item):
        with DB() as db:
            active = not db.checkActive(id_task)
            db.updateTask(id_task, active=active)
    return inner

def check_state(id_task):
    def inner(item):
        with DB() as db:
            return db.checkActive(id_task)
    return inner

def evento(*args):
    print("Evento disparado")    

def exit_action(icon):
    interrup.interrupted = True
    icon.visible = False
    icon.stop()    

def threaded_function(arg):
    while not interrup.interrupted:
        with DB() as db:
            for task in db.nextTask():
                id_exec = db.insertExec(task[0])                 
                result = subprocess.run(task[3], stdout=subprocess.PIPE)
                output = result.stdout.decode('utf-8')
                status = ""
                if (result.returncode == 0):
                    status = db.STATUS_FINISHED
                else:
                    status = db.STATUS_ERROR
                dt_last_exec=db.now()
                db.updateExec(id_exec, status, output, dt_last_exec, result.returncode)
                db.updateTask(task[0], dt_last_exec)
        time.sleep(60)
        

interrup = None
def callback(icon):
    #image = Image.new('RGBA', (128,128), (255,255,255,255)) # create new image
    #percent = 100
    thread = Thread(target = threaded_function, args=(None,))
    thread.start()
    while not interrup.interrupted:
        #if thread.isAlive():
            #step = 5
        #else:
            #step = 0
#            percent = 100
                        
        #img = image.copy()
        #d = ImageDraw.Draw(img)
        #d.rectangle([0, 128, 128, 128-(percent * 128) / 100], fill='blue')
        
        #percent -= step
        #if percent < 0:
            #percent = 100
        #icon.icon = img
        time.sleep(10)
    
    if thread.isAlive():
        thread.join()
    exit_action(icon)

def importTaks():
    with DB() as db:
        db.create()
        for f in glob.glob("./tasks/*.*", recursive=True):
            if "_" in f and f.endswith(".py"):                
                filepath = path.abspath(f)
                filename = path.basename(filepath)
                task = filename.replace(".py", "").split("_")            
                db.insertTask(
                    name=task[1],
                    interval=task[0],
                    cmd='python "{0}"'.format(filepath),
                    active=1
                )

def getTaskItems():
    taskItems = []
    with DB() as db:
        db.create()
        tasks = db.listTask()    
        for task in tasks:
            taskItems.append(
                pystray.MenuItem(
                    '{0} - {1}: {2}'.format(
                        task[0], 
                        task[1],
                        task[2]
                    ),
                    action = on_clicked(task[0]),
                    checked= check_state(task[0])
                )
            )
    return taskItems

importTaks()
taskItems = getTaskItems()
taskItems.append(
    pystray.MenuItem(                           
        'Exit',                                 
        exit_action
    )                                       
)

icon = pystray.Icon(                                    
    'Antoher Python Task Scheduler',                    
    create_image(),                                     
    menu = taskItems
)    

with GracefulInterruptHandler() as i:
    interrup = i
    icon.title = 'Antoher Python Task Scheduler'
    icon.visible = True    
    icon.run(setup=callback)

