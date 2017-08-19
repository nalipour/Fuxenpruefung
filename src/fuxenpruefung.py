import os
import random
import subprocess
import sys
import zipfile
from time import sleep

import tkinter as tk
from tkinter import filedialog, simpledialog

import i18n
import gui


def resource_path(basePath, relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relativePath)


def change_catagories(category, categoryUpdate):
    for key in categoryUpdate.keys():
        try:
            idx = list(map(lambda a: a[2], category)).index(key)
        except ValueError:
            continue
        category[idx][0] = categoryUpdate[key]
    return category


def switch_language(lang):
    if lang == 'ger':
        return 'eng'
    elif lang == 'eng':
        return 'bay'
    elif lang == 'bay':
        return 'ger'


taskVar = 0
zipPasswd = ''
questionFile = ''
lang = 'ger'
categoryUpdate = {}
while True:

    foxIco = resource_path('', r'images\fox.ico')
    foxPng = resource_path('', r'images\fox.png')
    lang_png_name = lang + '_' + switch_language(lang)
    lang_button_png = resource_path('', 'images\\' + lang_png_name + '.png')
    github_button_png = resource_path('', 'images\github.png')
    pngList = [foxPng, lang_button_png, github_button_png]

    categories = [
                  [16, i18n.longNames[lang][0], i18n.shortNames[lang][0]],
                  [6, i18n.longNames[lang][1], i18n.shortNames[lang][1]],
                  [4, i18n.longNames[lang][2], i18n.shortNames[lang][2]],
                  [1000, i18n.longNames[lang][3], i18n.shortNames[lang][3]],
                  [5, i18n.longNames[lang][4], i18n.shortNames[lang][4]],
                  [0, i18n.longNames[lang][5], i18n.shortNames[lang][5]],
                 ]
    change_catagories(categories, categoryUpdate)
    mainroot = tk.Tk()
    mainroot.iconbitmap(foxIco)
    mainroot.title('Fux!')
    mainapp = gui.InitWindow(mainroot, categories, lang, pngList, taskVar)
    mainroot.focus_force()
    mainroot.mainloop()
    if mainapp.switch_lang.get():
        lang = switch_language(lang)
    if mainapp.reinit.get():
        mainroot.destroy()
        continue
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

    # ask for question file
    FILEOPENOPTIONS = dict(initialdir='.', defaultextension='.txt', filetypes=[('', '*.txt;*.zip')])
    if not questionFile:
        questionFile = filedialog.askopenfilename(parent=mainroot, **FILEOPENOPTIONS)

    passwordError = False
    if questionFile.endswith('.zip'):
        zf = zipfile.ZipFile(questionFile)
        for zinfo in zf.infolist():
            isEncrypted = zinfo.flag_bits & 0x1
        if isEncrypted and zipPasswd == '':
            zipPasswd = simpledialog.askstring(i18n.passwordText[lang][0],
                                               i18n.passwordText[lang][1], show='*')
            try:
                zipPasswd_bytes = str.encode(zipPasswd)
            except TypeError:
                zipPasswd_bytes = b'1234'
            print(os.path.splitext(questionFile)[0])
            base = os.path.basename(questionFile)
            try:
                with zf.open(os.path.splitext(base)[0]+'.txt', pwd=zipPasswd_bytes) as data:
                    pass
            except RuntimeError:
                print('Bad password!')
                passwordError = True

    mainroot.destroy()

    if not questionFile or passwordError:
        errorIdx = 0
        if not questionFile:
            errorIdx = 0
        elif passwordError:
            errorIdx = 1
        root = tk.Tk()
        root.iconbitmap(foxIco)
        root.title(i18n.errorTitle[lang])
        lines = []
        lines.append(i18n.errorText[lang][errorIdx])
        app = gui.InfoWindow(root, lines)
        root.focus_force()
        root.mainloop()
        root.destroy()
        zipPasswd = ''
        questionFile = ''
        continue

    print('Selected task:', i18n.dictInit[lang][taskVar])

    # Read in data
    qdicts = {}
    for key in questNumbers.keys():
        qdicts[key] = {}
    qdictsAll = {}

    questCounter = 0
    questLines = []
    if questionFile.endswith('.zip'):
        base = os.path.basename(questionFile)
        with zf.open(os.path.splitext(base)[0]+'.txt', pwd=zipPasswd_bytes) as data:
            for byteLine in data:
                line = byteLine.decode('utf8')
                questLines.append(line)
    else:
        with open(questionFile, 'r', encoding='utf8') as data:
            for line in data:
                questLines.append(line)

    for line in questLines:
        line = line.rstrip()
        if line.startswith('#') or not len(line):
            continue
        splitlist = []
        try:
            splitlist = line.split("#", 4)
        except ValueError:
            continue
        splitlist = [x for x in map(lambda a: a.strip(), splitlist)]
        try:
            difficulty, question, answer, category, vspace = splitlist
        except ValueError:
            errorIdx = 2
            root = tk.Tk()
            root.iconbitmap(foxIco)
            root.title(i18n.errorTitle[lang])
            lines = []
            lines.append(i18n.errorText[lang][errorIdx] + ' ' + line)
            app = gui.InfoWindow(root, lines)
            root.focus_force()
            root.mainloop()
            root.destroy()
            zipPasswd = ''
            questionFile = ''
            continue

        qdicts[difficulty][len(qdicts[difficulty])] = question, answer, category, vspace
        qdictsAll[questCounter] = question, answer, category, difficulty, vspace
        questCounter += 1

    # process tasks below
    if taskVar == 0:
        ran_qdicts = {}
        for qdict_str in qdicts:
            qdict = qdicts[qdict_str]
            keys = list(qdict.keys())
            random.shuffle(keys)
            ran_QnA = [(qdict[key][:2]+(qdict[key][3],)) for key in keys][:questNumbers[qdict_str]]
            ran_qdicts[qdict_str] = ran_QnA

        with open(i18n.examFile[lang][0], 'w', encoding='utf8') as myfile:
            print(i18n.examTitle[lang][0]+"\n", file=myfile)
            count = 0
            for default, longName, shortName in categories:
                for question, answer, vspace in ran_qdicts[shortName]:
                    count += 1
                    questionlines = question.split("\\\\")
                    print('{}.'.format(count), questionlines[0], file=myfile)
                    for item in questionlines[1:]:
                        print('\to '+item, file=myfile)
                    print('\n'*int(vspace), file=myfile)

        with open(i18n.examFile[lang][1], 'w', encoding='utf8') as myfile:
            print(i18n.examTitle[lang][1]+"\n", file=myfile)
            count = 0
            for default, longName, shortName in categories:
                for question, answer, vspace in ran_qdicts[shortName]:
                    count += 1
                    print('{}.'.format(count), answer, file=myfile)

        sys_command = 'notepad '+i18n.examFile[lang][1]
        subprocess.Popen(sys_command)
        sleep(0.1)
        sys_command = 'notepad '+i18n.examFile[lang][0]
        subprocess.Popen(sys_command)

    elif taskVar == 1:
        from collections import Counter
        tot_n_questions = len(qdictsAll)
        # create message
        lines = []
        lines.append(i18n.statisticsHeader[lang][0])
        lines.append(i18n.statisticsColHeader[lang])
        for default, longName, shortName in categories:
            lines.append((longName+': ', str(len(qdicts[shortName])),
                         '{:.0f} %'.format(100*len(qdicts[shortName])/tot_n_questions)))

        lines.append(i18n.statisticsHeader[lang][1])
        lines.append(i18n.statisticsColHeader[lang])
        count_dict = Counter([x[2] for x in qdictsAll.values()])
        keys = list(count_dict.keys())
        keys.sort()
        for key in keys:
            lines.append((key+': ', str(count_dict[key]),
                         '{:.0f} %'.format(100*count_dict[key]/tot_n_questions)))

        root = tk.Tk()
        root.iconbitmap(foxIco)
        root.title('Fux!')
        app = gui.InfoWindow(root, lines)
        root.focus_force()
        root.mainloop()
        root.destroy()

    elif taskVar == 2:

        header = i18n.allquestionsHeader[lang]
        lines = []
        lines.append(i18n.allquestionsColHeader[lang])
        for key in qdictsAll:
            lines.append((qdictsAll[key][0],
                          qdictsAll[key][1],
                          qdictsAll[key][2],
                          qdictsAll[key][3],
                          qdictsAll[key][4],
                          ))

        root = tk.Tk()
        root.iconbitmap(foxIco)
        root.title('Fux!')
        app = gui.TextWindow(root, header, lines)
        root.focus_force()
        root.mainloop()
        root.destroy()
