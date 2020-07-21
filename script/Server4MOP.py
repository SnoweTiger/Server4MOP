#  Copyright (c) 2020 under GPLv3. Author: Snowetiger

#  Name: Server for MOP (gTTS4MOP)
#  Version: 1.01

#  Description: Generation main.bundle and sounpackage.json for vacuum cleaner Xiaomi MOP (1C)
#  and run a file server for sharing them
#  Описание: Генерbhetn main.bundle и sounpackage.json для пылесоса Xiaomi MOP (1C)
# и запустить файловый сервер для их раздачи


# Исполняемый код. Старт
import json
import socket
import http.server
import socketserver
import os
import hashlib

#Генерируем main.bundle
def  main_bundle_maker(bundle_file,upload_dir,scr_dir,ip_adress,port):
    with open(f'{scr_dir}/{bundle_file}', 'r', encoding="utf-8") as f:
        main_bundle_orig=f.read()
    main_bundle = main_bundle_orig.replace(
        'http:/xxx.xxx.xxx.xxx:4000/soundpackage.json',
        f'http:/{ip_adress}:{port}/soundpackage.json'
    )
    with open (f'{upload_dir}/main.bundle', 'w', encoding="utf-8") as f:
      f.write(main_bundle)
    print('Main.bundle готов')

#Получаем размер архива и MD5
def get_tar_data(tar_name, upload_dir):
    tar_dir = upload_dir + '/' + tar_name
    tar_size = os.path.getsize(tar_dir)
    tar_md5 = hashlib.md5(open(tar_dir, 'rb').read()).hexdigest()
    return tar_size,tar_md5

#Генерируем soundpackage.json
def soundpackage_maker(scr_dir,upload_dir,soundpackage_file,local_ip, port): #, tar_name, tar_md5, tar_size):
    with open(f'{scr_dir}/{soundpackage_file}', 'r', encoding='utf-8') as f:
        soundpackage = json.load(f)

    # soundpackage['data']['voices'][1]['download'] = f'http://{local_ip}:{port}/{tar_name}.tar.gz'
    # soundpackage['data']['voices'][1]['md5sum'] = tar_md5
    # soundpackage['data']['voices'][1]['size'] = tar_size

    # "name": {
    #           "default": "gTTS 4 MOP"
    #         }


    default_voice_ru = {
				"icon": "https://ksyru0-eco.fds.api.xiaomi.com/productinfo/mi1c/voices/images/ru.png",
				"listen": "https://ksyru0-eco.fds.api.xiaomi.com/productinfo/mi1c/voices/listen/start_clean_ru.mp3",
				"name": {"default":"русский язык"},
				"desc":{},
				"download": "https://ksyru0-eco.fds.api.xiaomi.com/productinfo/mi1c/voices/package/ru.tar.gz",
				"md5sum": "28c851a6352257476d16a8bb42e8aed7",
				"size":1125041,
				"id": "RU"
			}

    print()
    print ('Собираю soundpackage.json (макс. 6 архивов)')
    id_list = ['ES', 'FR', 'IT', 'DE', 'KO', 'ZH']
    id = 0

    # print('Имя архива (Размер, MD5)')
    print(f'{"Имя":15} ({"Размер":8}, {"MD5":32})')
    for file in os.listdir(upload_dir):
        if file.endswith(".tar.gz"):
            tar_data = get_tar_data(file, upload_dir)
            tar_size = tar_data[0]
            tar_md5 = tar_data[1]

            json_id = id + 2

            soundpackage['data']['voices'].append({
				"icon": "https://ksyru0-eco.fds.api.xiaomi.com/productinfo/mi1c/voices/images/ru.png",
				"listen": "https://ksyru0-eco.fds.api.xiaomi.com/productinfo/mi1c/voices/listen/start_clean_ru.mp3",
				"name": {"default":"русский язык"},
				"desc":{},
				"download": "tar path",
				"md5sum": "md5",
				"size":0,
				"id": "id"
			})

            if file[:-7] == 'tts4mop' :
                soundpackage['data']['voices'][json_id]["name"]["default"] = 'GoogleTTS for MOP(1C)'
            elif file[:-7] == 'ru' :
                soundpackage['data']['voices'][json_id]["name"]["default"] = 'Русский язык (не оригинал)'
            else:
                soundpackage['data']['voices'][json_id]["name"] = file[:-7]
            soundpackage['data']['voices'][json_id]['download'] = f'http://{local_ip}:{port}/{file[:7]}.tar.gz'
            soundpackage['data']['voices'][json_id]['md5sum'] = tar_md5
            soundpackage['data']['voices'][json_id]['size'] = tar_size
            soundpackage['data']['voices'][json_id]['id'] = id_list[id]

            print(f'{file:15} ({tar_size:8}, {tar_md5})')
            # print('{:{width}}'.format('Hi!', width=100),'{:{width}}'.format('Hi!', width=100))
            id = id + 1
            if id == 6: break #Достигнут максимум id (id = RU и EN не переписываем)

    # print(soundpackage['data']['voices'][3]["id"])
    # print(soundpackage['data']['voices'][4]["id"])

    with open(f'{upload_dir}/soundpackage.json', 'w', encoding="utf-8") as f:
        json.dump(soundpackage, f, sort_keys=True, indent=2, ensure_ascii=False)
    print()
    print(f'soundpackage.json готов, добавлено {id} архивов')
    print(f'Всего {id + 2} озвучек (включая стоковые RU, EN)')



TEMP_DIR = 'temp'
UPLOAD_DIR = 'upload'
SCR_DIR = 'scr'
TAR_NAME = 'tts4mop'
RU_TAR_FILE = 'ru.tar.gz'
BUNDLE_FILE = 'bundle.sdat'
SOUNDPACKAGE_FILE = 'soundpackage.sdat'



local_ip = socket.gethostbyname(socket.gethostname())
port = 80

main_bundle_maker(BUNDLE_FILE,UPLOAD_DIR,SCR_DIR,local_ip,port)
soundpackage_maker(SCR_DIR,UPLOAD_DIR,SOUNDPACKAGE_FILE,local_ip,port) #, TAR_NAME,tar_md5, tar_size) #(scr_dir,upload_dir,soundpackage_file,local_ip, port, tar_name, tar_md5, tar_size):

#Старт сервера
os.chdir(UPLOAD_DIR)
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", port), Handler)
print (f'Сервер запущен: {local_ip}:{port}')
print (f'Для остановки закройте приложение/остановите скрипт')
httpd.serve_forever()



