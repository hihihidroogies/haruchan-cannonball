import pygame as pg
import sys
from pygame.locals import *
import math
import random
import time

pg.init()

screen = pg.display.set_mode((1200, 800))

fps = 180
spd_div = 5 # 大きいほど時間を細分（判定が細かくなり、遅くなる）
wait_time = 5 # 飛行中の描画1回あたりの待機時間。大きいほど遅くなる

text = ''

font_path = 'files/ipaexg00401/ipaexg.ttf'

font = pg.font.Font(font_path, 28)
msgfont = pg.font.Font(font_path, 140)
scorefont = pg.font.Font(font_path, 40)

mortar = [
    pg.image.load('files/haru_ready.png'),
    pg.image.load('files/mortar96x96.png'),
    pg.image.load('files/mortar_launching1.png'),
    pg.image.load('files/mortar_launching2.png'),
    pg.image.load('files/mortar_launching3.png'),
]

mortar_base = pg.Surface((mortar[0].get_width()*2, mortar[0].get_height()*2), pg.SRCALPHA)
dodai = pg.image.load('files/dodai.png')
dodai = pg.transform.scale(dodai, (60, 60))

img_dummy = pg.Surface((0, 0))

haru_face = pg.image.load('files/haru_face.png')
haru_face_size = 50
haru_face = pg.transform.scale(haru_face, (haru_face_size, haru_face_size))

haru = [
    img_dummy,
    img_dummy,
    pg.image.load('files/haru_flying1.png'),
    pg.image.load('files/haru_flying2.png'),
    pg.image.load('files/haru_flying3.png'),
    pg.image.load('files/haru_touch_down.png'),
    pg.image.load('files/haru_crashed.png'),
    pg.image.load('files/haru_thumbs_up.png')
]
haru_size_x = 10
haru_size_y = 80
haruimg_size = 80
haru_tu_size = 90
for i in range(len(haru)):
    if i == 0:
        pass
    else:
        haru[i] = pg.transform.scale(haru[i], (haruimg_size, haruimg_size))


initial_haru_x = 100
initial_haru_y = 547
harurect = pg.Rect(initial_haru_x, initial_haru_y, haru_size_x, haru_size_y)
haru[7] = pg.transform.scale(haru[7], (haru_tu_size, haru_tu_size))

rabi = [
    pg.image.load('files/rabi_preparing.png'),
    pg.image.load('files/rabi_shooting1.png'),
    pg.image.load('files/rabi_shooting2.png'),
    pg.image.load('files/rabi_missed.png')
]
rabi_size = 8
for i in range(len(rabi)):
    rabi[i] = pg.transform.scale(rabi[i], (haruimg_size+rabi_size, haruimg_size+rabi_size))

wall_width = 100

tgt_width = wall_width
tgt = pg.Rect(0, 0, tgt_width, 1)
tgt_col = 0
img_tgt = pg.image.load('files/banana.png')
img_tgt = pg.transform.scale(img_tgt, (wall_width-40, wall_width-40))

trap = pg.Rect(0, 0, wall_width, 400)

wall = []
for i in range(5):
    wall.append(pg.Rect(400+i*140, 0, wall_width, 800))

building_roof = pg.image.load('files/building_roof.png')
building_roof = pg.transform.scale(building_roof, (wall_width, wall_width))
building_wall = pg.image.load('files/building_wall.png')
building_wall = pg.transform.scale(building_wall, (wall_width, wall_width))

building = pg.Surface((wall_width, 800))
building.blit(building_roof, [0, 0])
for i in range(7):
    building.blit(building_wall, [0, wall_width*(i+1)])

bg = pg.image.load('files/bg.png')
bg = pg.transform.scale(bg, (1200, 800))
bg_surface = pg.Surface((1200, 800))
bg_surface.blit(bg, [0, 0])

WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
BLUE  = (  0,   0, 255)
TOMATO= (255, 99,   71)
BLINK = [WHITE, pg.Color('gold')]

score = 0

idx = 8
go_to = 8
help_idx = 0

elevation = 40 # 仰角
rotation = 40 # 臼砲画像の傾き

power = 0 # 表示するパワー
act_power = 0 # 発射時の実際のパワー
power_gage = 0

flying = 0 # 飛行中であるかどうか
vx, vy = 0, 0 # 移動量

extra_ammo_point = 500 # 何ポイントごとに弾薬を追加するか

ammo = 10
bonus = 1
add_score = 0
tmr = 0
haruimg = 0
enter_release_flag = 0
saved_flag = 0
loaded_flag = 0
wait_flag = 0
high_score_flag = 0
wait_time1 = 0
wait_time2 = 0
text_flag = 0
redraw_flag = 0
help_position = 310

file = ''
r1 = ''


def draw_screen(haru_numb, rabi_numb, mortar_numb):
    if redraw_flag == 1:
        screen.blit(bg_surface, [0, 0])
        for i in range(5):
            screen.blit(building, wall[i])
        screen.blit(rabi[rabi_numb], [-10-rabi_size, 540-rabi_size])
        #pg.draw.rect(screen, pg.Color('BLUE'), harurect)
        mortar_bg = pg.Surface((mortar[mortar_numb].get_width()*2, mortar[mortar_numb].get_height()*2), pg.SRCALPHA)
        mortar_bg.blit(mortar[mortar_numb], [mortar[mortar_numb].get_width(), mortar[mortar_numb].get_height()/2])
        mortar_bg = pg.transform.rotate(mortar_bg, rotation)
        screen.blit(mortar_bg, [100-mortar_bg.get_width()/2, 600-mortar_bg.get_height()/2])
        screen.blit(dodai, [69, 560])
        if haru_numb == 7:
            screen.blit(haru[haru_numb], [harurect.x+haru_size_x/2-haruimg_size/2, harurect.y+harurect.height-haru_tu_size])
        else:
            screen.blit(haru[haru_numb], [harurect.x+haru_size_x/2-haruimg_size/2, harurect.y+haru_size_y-haruimg_size])
        screen.blit(img_tgt, [tgt.x+tgt_width/2-img_tgt.get_width()/2, tgt.y+3-img_tgt.get_height()])
        #pg.draw.rect(screen, pg.Color('red'), trap)
        #pg.draw.rect(screen, pg.Color('gold'), tgt)
        text = font.render('x{:<2}'.format(ammo)+'    得点倍率: '+str((add_score+100)/100)+'    SCORE:{:>5}'.format(score)+'    HIGH SCORE:{:>5}'.format(high_score), True, BLACK)
        screen.blit(text, [382, 31])
        text = font.render('x{:<2}'.format(ammo)+'    得点倍率: '+str((add_score+100)/100)+'    SCORE:{:>5}'.format(score)+'    HIGH SCORE:{:>5}'.format(high_score), True, WHITE)
        screen.blit(text, [380, 30])
        screen.blit(haru_face, [330, 10])
    if text_flag == 1:
        #pg.draw.rect(screen, (88,  92, 108), [148, 598, 380, 32])
        pg.draw.rect(screen, (88,  92, 108), [148, 598, 270, 32])
        text = font.render('仰角:{:>3}'.format(elevation)+' パワー:{:>3}'.format(power), True, BLACK)
        screen.blit(text, [152, 601])
        text = font.render('仰角:{:>3}'.format(elevation)+' パワー:{:>3}'.format(power), True, WHITE)
        screen.blit(text, [150, 600])
    if power_gage == 1:
        pg.draw.rect(screen, WHITE, [98, 648, 504, 84])
        pg.draw.rect(screen, BLUE, [100, 650, 500, 80])
        if power > 0:
            pg.draw.rect(screen, TOMATO, [100, 650, power*5, 80])


def draw_msg(result):
    text = msgfont.render(result, True, BLACK)
    screen.blit(text, [602-text.get_width()/2, 401-text.get_height()/2])
    text = msgfont.render(result, True, WHITE)
    screen.blit(text, [600-text.get_width()/2, 400-text.get_height()/2])
    if result == '成功！':
        text = scorefont.render('SCORE +'+str(100+add_score), True, BLACK)
        screen.blit(text, [602-text.get_width()/2, 501-text.get_height()/2])
        text = scorefont.render('SCORE +'+str(100+add_score), True, WHITE)
        screen.blit(text, [600-text.get_width()/2, 500-text.get_height()/2])
            

def main():
    global text, idx, tgt_x, tgt_y, tgt, tgt_col, wall, elevation, rotation, mortar_bg, power, act_power, power_gage, flying
    global vx, vy, score, tmr, ammo, enter_release_flag, saved_flag, high_score, file, r1, loaded_flag, wait_flag, high_score_flag
    global wait_time1, wait_time2, help_idx, text_flag, redraw_flag, add_score, help_position, go_to
    powerplus = 1
    
    pg.init()
    pg.display.set_caption('Haruchan Cannonball')
    screen = pg.display.set_mode((1200, 800))
    clock = pg.time.Clock()

    screen.blit(bg_surface, [0, 0])

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        key = pg.key.get_pressed()

        if idx == 0: # 壁とターゲットの配置
            if key[K_BACKSPACE] == 0 and key[K_RETURN] == 0:
                for i in range(len(wall)):
                    wall[i].y = 0
                for i in range(len(wall)): # 壁
                    if i == 0:
                        wall[i].y = 700 + random.randint(-150, 0)
                    else:
                        while 200 >= wall[i].y or wall[i].y > 700:
                            wall[i].y = wall[i-1].y + random.randint(-150, 100)
                tgt_col = random.randint(2, 4) # ターゲット
                tgt.x = 400+140*tgt_col+wall_width/2-tgt_width/2
                tgt.y = wall[tgt_col].y - tgt.height
                trap.x = tgt.x
                trap.y = tgt.y+20
                idx = 1
 
        if idx == 1: # 仰角の調整
            harurect.x = initial_haru_x # ハルの初期位置
            harurect.y = initial_haru_y
            if key[K_UP] == 1 and elevation < 85:
                elevation += 1
                rotation += 1
            if key[K_DOWN] == 1 and elevation > 5:
                elevation -= 1
                rotation -= 1
            mortar_bg = pg.Surface((mortar[0].get_width()*2, mortar[0].get_height()*2), pg.SRCALPHA)
            mortar_bg.blit(mortar[0], [mortar[0].get_width(), mortar[0].get_height()/2])
            mortar_bg = pg.transform.rotate(mortar_bg, rotation)
            text_flag = 1
            redraw_flag = 1
            draw_screen(0, 0, 0)
            text = font.render('[h]key : help', True, BLACK)
            screen.blit(text, [102, 31])
            text = font.render('[h]key : help', True, WHITE)
            screen.blit(text, [100, 30])
            if key[K_h] == 1:
                help_idx = 1
                idx = 10
            if key[K_RETURN] == 1:
                go_to = 3
                idx = 2
            if key[K_BACKSPACE] == 1 and ammo > 0:
                ammo -= 1
                add_score = 0
                idx = 0
                
        if idx == 2: # キー離し待ち
            if key[K_RETURN] == 0:
                idx = go_to
                
        if idx == 3: # パワーの調整
            if redraw_flag == 1:
                draw_screen(0, 0, 0)
                redraw_flag = 0
            power_gage = 1
            if key[K_RETURN] == 1:
                act_power = 50+power/2
                idx = 4
            elif key[K_RETURN] == 0:
                if powerplus == 1:
                    power += 1
                    if power >= 100:
                        powerplus = 0
                elif powerplus == 0:
                    power -= 1
                    if power <= 0:
                        powerplus = 1
            draw_screen(0, 0, 0)

        if idx == 4: # 飛行
            #print(key[K_RETURN])
            flying = 1
            #harurect.x = initial_haru_x # ハルの初期位置
            #harurect.y = initial_haru_y
            vx = int(math.cos(math.radians(elevation))*act_power)
            vy = - int(math.sin(math.radians(elevation))*act_power)
            haruimg = 0
            rabiimg = 0
            redraw_flag = 1
            tmr = 0
            
            while flying == 1:
                #print(key[K_RETURN])
                vy += 5 / spd_div # 重力加速度
                harurect.x += vx / spd_div
                harurect.y += vy / spd_div
                #print(vx, vy)
                if harurect.y <= -2000 or harurect.y > 1000: 
                    flying = 0 
                    
                pg.display.update()
                pg.time.wait(wait_time)
                
                tmr += 1

                #ハルの画像
                if vy < -10:
                    haruimg = 2
                elif -10 <= vy and vy < 5:
                    haruimg = 3
                elif 5 <= vy:
                    haruimg = 4
                if tmr < 5:
                    haruimg = 0

                #ラビの画像
                if tmr > 30:
                    rabiimg = 0
                elif tmr > 15:
                    rabiimg = 2
                elif tmr > 0:
                    rabiimg = 1

                #臼砲の画像
                if tmr > 30:
                    mortarimg = 1
                elif tmr > 20:
                    mortarimg = 4
                elif tmr > 10:
                    mortarimg = 3
                elif tmr > 0:
                    mortarimg = 2

                if harurect.colliderect(trap):
                    flying = 0
                    draw_screen(6, 3, 1)
                    draw_msg('失敗')
                    pg.display.update()
                    ammo -= 1
                    add_score += 50
                    pg.time.wait(500)
                    if ammo < 0:
                        ammo = 0
                        add_score = 0
                        idx = 6
                        break
                    go_to = 1
                    idx = 2
                    break
                elif harurect.colliderect(tgt): # 命中
                    flying = 0
                    ex_score = score
                    score += 100+add_score
                    if score > high_score:
                        high_score = score
                        high_score_flag = 1
                    draw_screen(5, 0, 1)
                    draw_msg('成功！')
                    pg.display.update()
                    pg.time.wait(500)
                    draw_screen(7, 0, 1)
                    draw_msg('成功！')
                    pg.display.update()
                    pg.time.wait(500)
                    ammo_plus = score // extra_ammo_point - ex_score // extra_ammo_point # エクストラハル
                    if ammo_plus > 0:
                        ammo += ammo_plus
                        draw_screen(7, 0, 1)
                        text = scorefont.render('ボーナス', True, BLACK)
                        screen.blit(text, [602-text.get_width()/2, 401-text.get_height()/2])
                        text = scorefont.render('ボーナス', True, WHITE)
                        screen.blit(text, [600-text.get_width()/2, 400-text.get_height()/2])
                        text = scorefont.render('     +'+str(ammo_plus), True, BLACK)
                        screen.blit(text, [602-text.get_width()/2, 451-text.get_height()/2])
                        text = scorefont.render('     +'+str(ammo_plus), True, WHITE)
                        screen.blit(text, [600-text.get_width()/2, 450-text.get_height()/2])
                        screen.blit(haru_face, [552, 422])
                        pg.display.update()
                        pg.time.wait(1000)
                        ammo_plus = 0
                    add_score = 0
                    idx = 0
                    break
                elif harurect.collidelistall(wall): # クラッシュ
                    flying = 0
                    draw_screen(6, 3, 1)
                    draw_msg('失敗')
                    pg.display.update()
                    ammo -= 1
                    add_score += 50
                    pg.time.wait(500)
                    if ammo < 0:
                        ammo = 0
                        add_score = 0
                        idx = 6
                        break
                    go_to = 1
                    idx = 2
                    break
                elif harurect.x >= 1300 or harurect.y >= 900: # 外れた
                    flying = 0
                    draw_screen(1, 3, 1)
                    draw_msg('失敗')
                    pg.display.update()
                    ammo -= 1
                    add_score += 50
                    pg.time.wait(500)
                    if ammo < 0:
                        ammo = 0
                        add_score = 0
                        idx = 6
                        break
                    go_to = 1
                    idx = 2
                    break
                else: 
                    draw_screen(haruimg, rabiimg, mortarimg)
            power = 0
            act_power = 0
            power_gage = 0
            
        if idx == 6: # ゲームオーバー
            if key[K_RETURN] == 0:
                if wait_flag == 0:
                    wait_time1 = time.time()
                    wait_flag = 1
                wait_time2 = time.time()
                text_flag = 0
                draw_screen(0, 0, 1)
                draw_msg('GAME OVER')
                text = scorefont.render('SCORE: '+str(score), True, BLACK)
                screen.blit(text, [602-text.get_width()/2, 501-text.get_height()/2])
                text = scorefont.render('SCORE: '+str(score), True, WHITE)
                screen.blit(text, [600-text.get_width()/2, 500-text.get_height()/2])
                if high_score_flag == 1:
                    tmr += 1
                    if tmr >= 2:
                        tmr = 0
                    text = scorefont.render('HIGH SCORE', True, BLACK)
                    screen.blit(text, [602-text.get_width()/2, 541-text.get_height()/2])
                    text = scorefont.render('HIGH SCORE', True, BLINK[tmr])
                    screen.blit(text, [600-text.get_width()/2, 540-text.get_height()/2])
                    if saved_flag == 0:
                        file = open('files/high_score.txt', 'w')
                        file.write(str(score))
                        file.close()
                        saved_flag = 1
                pg.display.update()
                enter_release_flag = 1
            if key[K_RETURN] == 1 and enter_release_flag == 1 and wait_time2 - wait_time1 > 1.5:
                saved_flag = 0
                high_score_flag = 0
                enter_release_flag = 0
                wait_flag = 0
                idx = 7

        if idx == 7: # 初期化、キー離し待ち
            power = 0
            act_power = 0
            power_gage = 0
            score = 0
            ammo = 10
            elevation = 40
            rotation = 40
            flying = 0
            tmr = 0
            if key[K_RETURN] == 0:
                idx = 8

        if idx == 8: # タイトル画面
            if loaded_flag == 0:
                file = open('files/high_score.txt', 'r')
                r1 = file.read()
                file.close()
                high_score = int(r1)
                loaded_flag = 1
            screen.blit(bg_surface, [0, 0])
            text = msgfont.render('Haruchan', True, BLACK)
            screen.blit(text, [152, 246])
            text = msgfont.render('Haruchan', True, pg.Color('orange'))
            screen.blit(text, [150, 245])
            text = msgfont.render('Cannonball', True, BLACK)
            screen.blit(text, [362, 371])
            text = msgfont.render('Cannonball', True, pg.Color('orange'))
            screen.blit(text, [360, 370])
            text = font.render('x{:<2}'.format(ammo)+'    得点倍率: '+str((add_score+100)/100)+'    SCORE:{:>5}'.format(score)+'    HIGH SCORE:{:>5}'.format(high_score), True, BLACK)
            screen.blit(text, [382, 31])
            text = font.render('x{:<2}'.format(ammo)+'    得点倍率: '+str((add_score+100)/100)+'    SCORE:{:>5}'.format(score)+'    HIGH SCORE:{:>5}'.format(high_score), True, WHITE)
            screen.blit(text, [380, 30])
            screen.blit(haru_face, [330, 10])
            text = scorefont.render('ENTERキーでスタート', True, BLACK)
            screen.blit(text, [602-text.get_width()/2, 601])
            text = scorefont.render('ENTERキーでスタート', True, WHITE)
            screen.blit(text, [600-text.get_width()/2, 600])
            text = font.render('[h]key : help', True, BLACK)
            screen.blit(text, [102, 31])
            text = font.render('[h]key : help', True, WHITE)
            screen.blit(text, [100, 30])
            if key[K_h] == 1:
                help_idx = 8
                idx = 10
            if key[K_RETURN] == 1:
                loaded_flag = 0
                go_to = 0
                idx = 2

        if idx == 10: # ヘルプ画面
            screen.blit(bg_surface, [0, 0])
            help_position = 310
            text = scorefont.render('↑ または ↓ : 仰角の調整', True, BLACK)
            screen.blit(text, [602-text.get_width()/2, help_position+1])
            text = scorefont.render('↑ または ↓ : 仰角の調整', True, WHITE)
            screen.blit(text, [600-text.get_width()/2, help_position])
            text = scorefont.render('ENTER : 射出', True, BLACK)
            screen.blit(text, [602-text.get_width()/2, help_position+51])
            text = scorefont.render('ENTER : 射出', True, WHITE)
            screen.blit(text, [600-text.get_width()/2, help_position+50])
            text = scorefont.render('BACKSPACE :      を1消費してステージをスキップ', True, BLACK)
            screen.blit(text, [602-text.get_width()/2, help_position+101])
            text = scorefont.render('BACKSPACE :      を1消費してステージをスキップ', True, WHITE)
            screen.blit(text, [600-text.get_width()/2, help_position+100])
            screen.blit(haru_face, [420, help_position+92])
            text = scorefont.render('500ポイントごとに       を1獲得', True, BLACK)
            screen.blit(text, [602-text.get_width()/2, help_position+151])
            text = scorefont.render('500ポイントごとに       を1獲得', True, WHITE)
            screen.blit(text, [600-text.get_width()/2, help_position+150])
            screen.blit(haru_face, [682, help_position+142])
            pg.display.update()
            if key[K_h] == 0:
                idx = help_idx

        pg.display.update()
        pg.time.Clock().tick(fps)


if __name__ == '__main__':
    main()
