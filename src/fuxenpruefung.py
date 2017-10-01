import os
import sys
import zipfile

import tkinter as tk
from tkinter import filedialog, simpledialog

import data
import i18n
import gui
import files
import tasks
try:
    import sound_linux as sound
except ImportError:
    import sound_win as sound


def change_catagories(category, categoryUpdate):
    for key in categoryUpdate.keys():
        try:
            idx = list(map(lambda a: a[2], category)).index(key)
        except ValueError:
            continue
        category[idx][0] = categoryUpdate[key]
    return category


sound.start_sound()
taskVar = 0
zipPasswd = ''
questionFile = ''
categoryUpdate = {}
foxIco = files.resource_path('', r'images\fox.ico')


while True:

    lang_button_png = i18n.lang_button_image()
    sound_buttong_png = sound.sound_button_image()

    categories = [
                  [16, i18n.longNames[i18n.lang()][0], i18n.shortNames[i18n.lang()][0]],
                  [6, i18n.longNames[i18n.lang()][1], i18n.shortNames[i18n.lang()][1]],
                  [4, i18n.longNames[i18n.lang()][2], i18n.shortNames[i18n.lang()][2]],
                  [1000, i18n.longNames[i18n.lang()][3], i18n.shortNames[i18n.lang()][3]],
                  [5, i18n.longNames[i18n.lang()][4], i18n.shortNames[i18n.lang()][4]],
                  [0, i18n.longNames[i18n.lang()][5], i18n.shortNames[i18n.lang()][5]],
                 ]
    change_catagories(categories, categoryUpdate)
    category_numbers = map(lambda x: x[0], categories)
    mainroot = tk.Tk()
    if sys.platform == 'win32':
        mainroot.iconbitmap(foxIco)
    mainroot.title('Fux!')
    mainapp = gui.InitWindow(mainroot, category_numbers, taskVar)
    mainroot.focus_force()
    mainroot.mainloop()
    taskVar = mainapp.radio_var.get()
    idx = 0
    questNumbers = {}
    for idx, thisCat in enumerate(categories):
        default, longName, shortName = thisCat
        try:
            questNumbers[shortName] = categoryUpdate[shortName] = int((mainapp.inputDict)[shortName].get())
        except KeyError:
            questNumbers[shortName] = default
        categories[idx][0] = questNumbers[shortName]
        idx += 1

    print('Selected task:', i18n.dictInit[i18n.lang()][taskVar])

    if taskVar == 4:
        mainroot.destroy()
        tasks.play_snake()
        continue

    # ask for question file
    FILEOPENOPTIONS = dict(initialdir='.', defaultextension='.txt', filetypes=[('', '*.txt;*.zip')])
    if not questionFile:
        questionFile = filedialog.askopenfilename(parent=mainroot, **FILEOPENOPTIONS)

    passwordError = False
    if questionFile != () and questionFile.endswith('.zip'):
        zipFile = zipfile.ZipFile(questionFile)
        for zinfo in zipFile.infolist():
            isEncrypted = zinfo.flag_bits & 0x1
        if isEncrypted and zipPasswd == '':
            zipPasswd = simpledialog.askstring(i18n.passwordText[i18n.lang()][0],
                                               i18n.passwordText[i18n.lang()][1], show='*')
            try:
                zipPasswd_bytes = str.encode(zipPasswd)
            except TypeError:
                zipPasswd_bytes = b'1234'
            print(os.path.splitext(questionFile)[0])
            base = os.path.basename(questionFile)
            try:
                with zipFile.open(os.path.splitext(base)[0]+'.txt', pwd=zipPasswd_bytes):
                    pass
            except RuntimeError:
                print('Bad password!')
                passwordError = True
    else:
        zipFile = ''

    mainroot.destroy()

    if passwordError:
        errorIdx = 1
        root = tk.Tk()
        if sys.platform == 'win32':
            root.iconbitmap(foxIco)
        root.title(i18n.errorTitle[i18n.lang()])
        lines = []
        lines.append(i18n.errorText[i18n.lang()][errorIdx])
        app = gui.InfoWindow(root, lines)
        root.focus_force()
        root.mainloop()
        root.destroy()
        zipPasswd = ''
        questionFile = ''
        continue

    if not questionFile:
        continue

    qdicts, qdictsAll = data.read_data(questNumbers, questionFile, zipFile, zipPasswd)

    # process tasks below
    if taskVar == 0:
        tasks.new_exam(qdicts, questNumbers, categories)

    elif taskVar == 1:
        tasks.show_statistics(qdicts, qdictsAll, categories)

    elif taskVar == 2:
        tasks.show_questions(qdictsAll)

    elif taskVar == 3:
        tasks.interactive_quiz(qdicts, questNumbers)
