import requests
import re, cv2, moviepy
from moviepy.editor import AudioFileClip, concatenate_videoclips, VideoFileClip


# Отправляем loadit.xyz запрос на обработку
def get_url(id, loop):
    if loop != 0:
        url = 'https://api.loadit.xyz/compile?url=https:%2F%2Fcoub.com%2Fview%2F' + str(id) + '&loops=' + str(loop)
    else:
        url = 'https://api.loadit.xyz/compile?url=https:%2F%2Fcoub.com%2Fview%2F' + str(id)

    request = requests.get(url)
    download_url = request.text
    download_url = re.sub('"', '', download_url)
    return (download_url)


# Скачиваем файл с loadit.xyz
def downloadfile(name, url):
    name = name + ".mp4"
    try:
        r = requests.get(url)
        print("Connected to " + url)
        f = open("content/" + name, 'wb');
        print("Donloading.....")
        for chunk in r.iter_content(chunk_size=255):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
        print("Done")
        f.close()
    except:
        print('Не удалось скачать: ' + url)


# Возвращает dict {coub_id: coub_duration}
def get_list_from_coub(week_url):
    coubs_list = {}
    requset = requests.get(week_url)
    dict = requset.json()
    for key in dict["coubs"]:
        coubs_list.update({key["permalink"]: key["duration"]})
    page_count = 2
    while dict["total_pages"] >= page_count:
        week_url_page = week_url + '?page=' + str(page_count)
        requset = requests.get(week_url_page)
        dict = requset.json()
        for key in dict["coubs"]:
            coubs_list.update({key["permalink"]: key["duration"]})
        page_count += 1

    return coubs_list


# Объединяем предыдущие функции. На выходе готовые видео - кубы. Возвращает coubes_list
def coubs_download(week_url):  # Объединяем предыдущие функции. На выходе готовые видео - кубы.
    cubes_list = get_list_from_coub(week_url)
    numb = 0
    for id_duration in cubes_list:
        if cubes_list[id_duration] <= 1:
            loop = 10
        elif cubes_list[id_duration] <= 2:
            loop = 5
        elif cubes_list[id_duration] <= 3:
            loop = 3
        elif cubes_list[id_duration] <= 4:
            loop = 2
        elif cubes_list[id_duration] <= 5:
            loop = 2
        elif cubes_list[id_duration] <= 6:
            loop = 2
        else:
            loop = 0
        clear_url = get_url(id_duration, loop)
        downloadfile(id_duration, clear_url)
        numb += 1
    return cubes_list


def create_full_video(coub_names, final_video_name):  # Передать спиоск названий кубов. Выход - готовое видео.


    ##
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Video Coding
    fps = 25  # cap.get(cv2.CAP_PROP_FPS)  # Getting video's FPS
    connect_names=[]
    # tihs for is a for for a background video
    between = VideoFileClip('content/between.mp4')  # Reading the video
    check=0
    for a in coub_names:
        if check >=60: 
            print('last coub_id: '+str(a))
            break
        check +=1
        try:
            out = cv2.VideoWriter('content/ready/temp/' + a + '.mp4', fourcc, fps, (1920, 1080))
            cap = cv2.VideoCapture('content/' + a + '.mp4')  # Reading the video

            audioclip = AudioFileClip('content/' + a + '.mp4')
            # Define the codec and create VideoWriter object
            breaking = 1

            while (cap.isOpened()):
                ret, frame = cap.read()
                if ret == True:
                    if frame.shape[1] / frame.shape[0] == 16 / 9:
                        frame = cv2.resize(frame, (1920, 1080))
                    else:
                        frame_not_blur = frame
                        frame = cv2.blur(frame, (15, 15))
                        frame = cv2.resize(frame, (1920, 1080))
                        if frame_not_blur.shape[1] > frame_not_blur.shape[0]:
                            x_width = int(1080 / (frame_not_blur.shape[0] / frame_not_blur.shape[1]))
                        else:
                            x_width = int(1080 / (
                                frame_not_blur.shape[1] / frame_not_blur.shape[0]))  # считаем пропорциональную ширину
                        if x_width > 1920: #Если ширина больше 1920, резайзим
                            x_height = int(1920*1080/x_width)
                            x_width = 1920
                            frame_not_blur = cv2.resize(frame_not_blur, (x_width, x_height))
                            ball = frame_not_blur[0:frame_not_blur.shape[0], 0:frame_not_blur.shape[1]]  # достаем квадрат
                            y_pos = int(1080 / 2 - frame_not_blur.shape[0] / 2)
                            frame = cv2.rectangle(frame,(0,1080),(0,1920),(0,0,0),3) #вставляем на фон черный квадрат 1920х1080
                            frame[0+y_pos:frame_not_blur.shape[0]+y_pos,0:frame_not_blur.shape[1]] = ball
                        else:
                            frame_not_blur = cv2.resize(frame_not_blur, (x_width, 1080))
                            ball = frame_not_blur[0:frame_not_blur.shape[0], 0:frame_not_blur.shape[1]]  # достаем квадрат
                            x_pos = 1920 / 2 - frame_not_blur.shape[1] / 2
                            x_pos = int(x_pos)
                            frame[0:frame_not_blur.shape[0],0 + x_pos:frame_not_blur.shape[1] + x_pos] = ball  # вставляем квадрат

                    # write the flipped frame
                    out.write(frame)

                    #breaking = 0  # Чтоб кастовался следующий while

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break

            cap.release()
            out.release()
            cv2.destroyAllWindows()
            video = VideoFileClip('content/ready/temp/' + a + '.mp4')
            final_clip = video.set_audio(audioclip)
            #final_clip.write_videofile('content/ready/temp/result/' + a + '.mp4')
            connect_names.append(final_clip)
            connect_names.append(between)
        except:
            print('Ошибка, файл: content/' + a + '.mp4')

    # Release everything if job is finished
    final_clip = concatenate_videoclips(connect_names)
    final_clip.write_videofile('content/ready/production/ANIME_HOT_HALF'+str(final_video_name)+'.mp4')



    #final_clip = video.set_audio(final_clip)
    #music.audio.write_audiofile('content/ready/' + str(final_video_name) + '_1.mp3')

    #final_clip.write_videofile('content/ready/' + str(final_video_name) + '_1.mp4')


    #final_clip.write_audiofile('content/ready/TEST_1.mp3')

import time

start_time = time.time()
count = 302
while count == 302:
    #week_url = 'https://coub.com/api/v2/weekly_digests/' + str(count) + '/coubs'
    #week_url = 'https://coub.com/api/v2/weekly_digests/303/coubs'
    week_url = 'https://coub.com/api/v2/timeline/hot/anime/half'
    #coub_names = coubs_download(week_url)
    coub_names = get_list_from_coub(week_url)
    print(coub_names)
    print(len(coub_names))
    create_full_video(coub_names, count)
    count = count - 1
    print(count)
    # cubes_list= coubs_download(week_url)
    # create_full_video(cubes_list)
    print("--- %s seconds---" % (time.time() - start_time))

# TEST1: BLUR 15 --- 296.7929756641388 seconds---
# TEST2: BLUR 10 --- 306.09150743484497 seconds---
# TEST3: BLUR 15
