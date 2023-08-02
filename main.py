import os
import sys
import shutil
import ctypes
from tkinter import *
from tkinter import font
from pathlib import Path
from functools import partial
from tkinter.scrolledtext import ScrolledText

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
elif __file__:
    application_path = os.path.dirname(__file__)

root = Tk()
root.iconbitmap(default=os.path.join(application_path, 'favicon.ico'))
# root.iconphoto(False, PhotoImage(file='favicon.png'))
root.title("Temporary Cleaner")
root.geometry("650x650")
root.resizable(False, False)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

VAR_LIST = []
FILES_TO_KEEP = set()
FILES_FRAME = None
SEARCH = None
SEARCH_BAR = None
TEMP_FOLDERS_PATH = ['C:/Windows/Temp/', f'C:/Users/{os.getlogin()}/AppData/Local/Temp/']

def br(master=root):
    Label(master, text="").pack()

def add_files_to_keep(file_path, index):
    if VAR_LIST[index].get() == 1:
        FILES_TO_KEEP.add(file_path)
    else:
        try:
            FILES_TO_KEEP.remove(file_path)
        except:
            pass

def human_size(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def clear_temps():
    deleteFileCount = 0
    deleteFolderCount = 0
    for folder in TEMP_FOLDERS_PATH:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            indexNo = file_path.find('\\')
            itemName = file_path[indexNo+1:]
            if folder+file not in FILES_TO_KEEP:
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f'{itemName} file deleted')
                        deleteFileCount = deleteFileCount + 1

                    elif os.path.isdir(file_path):
                        if file_path.__contains__('chocolatey'): 
                            continue
                        shutil.rmtree(file_path)
                        print(f'{itemName} folder deleted')
                        deleteFolderCount = deleteFolderCount + 1
                except Exception:
                    print(f'Access Denied: {itemName}')
            else:
                print(f'Skiping: {itemName}')
    scan_temp()

def scan_temp(search=""):
    global FILES_FRAME, VAR_LIST, FILES_TO_KEEP, SEARCH_BAR

    files, folders = 0, 0
    if FILES_FRAME:
        FILES_FRAME.config(state='normal')
        FILES_FRAME.delete(1.0, END)
    else:
        FILES_FRAME = ScrolledText(root, width=60, height=15, bg="grey", wrap=WORD)
        FILES_FRAME.pack()

    count = 0
    size = 0

    for temp in TEMP_FOLDERS_PATH:
        root_directory = Path(temp)
        size += sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())
        for file in os.listdir(temp):
            if search in file:
                if os.path.isfile(temp+file):
                    files += 1
                elif os.path.isdir(temp+file):
                    folders += 1
                VAR_LIST.append(IntVar(value=0))
                cb = Checkbutton(FILES_FRAME, variable=VAR_LIST[count], text=temp+file, bg="grey", fg="black", command=partial(add_files_to_keep, temp+file, count), font=("Cooper Black", 10), anchor='w')
                FILES_FRAME.window_create('end', window=cb)
                FILES_FRAME.insert('end', '\n')
                count += 1
    status['text'] = f"Status=> Files: {files} Folders: {folders}"
    storage_status['text'] = f"Size: {human_size(size)}"
    FILES_FRAME['state']='disabled'
    SEARCH_BAR.focus_set()

Label(root, text="Temporary Cleaner", fg="Blue", font=("Cooper Black", 45)).pack()

br()

STATUS_FRAME = Frame(root)
status = Label(STATUS_FRAME, text="Status: N/A", fg="Green", font=("Cooper Black", 20))
status.pack(side=LEFT)
storage_status = Label(STATUS_FRAME, text="Size: N/A", fg="Green", font=("Cooper Black", 20))
storage_status.pack(side=RIGHT)
STATUS_FRAME.pack(padx=5, fill=X)

br()
Label(root, text="Select files to keep.", fg="Black", font=("Cooper Black", 15)).pack()
br()

FONT = font.nametofont("TkDefaultFont") 
FONT.actual()
SEARCH_FRAME = Frame(root)
SEARCH_LABEL = Label(SEARCH_FRAME, text="Seach Files: ", fg="Black", font=(FONT, 12))
SEARCH = StringVar()
SEARCH_BAR = Entry(SEARCH_FRAME, textvariable=SEARCH, font=(FONT, 12))
SEARCH_BAR.bind('<KeyRelease>', lambda e: scan_temp(SEARCH.get()))
SEARCH_LABEL.pack(side=LEFT)
SEARCH_BAR.pack(side=LEFT)
SEARCH_FRAME.pack()

br()
scan_temp()
br()

Button(root, text="Refresh", font=("Cooper Black", 15), command=partial(scan_temp, SEARCH.get())).pack()
Button(root, text="Clear Temporary Files", font=("Cooper Black", 15), command=clear_temps).pack()

Label(root, text="Made with 💝 by @MrHydroCoder", font=("Cooper Black", 25)).pack(side=BOTTOM)

root.mainloop()