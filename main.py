#%%
import random, pygame, sys, cx_Freeze
from PIL import Image
from pygame.locals import *
from multiprocessing import Queue

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 8
BOXSIZE = 60
GAPSIZE = 10
BOARDWIDTH = 4
BOARDHEIGHT = 4
assert (BOARDWIDTH * BOARDWIDTH) % 2 == 0, '이미지 개수가 짝수'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE)))/2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE)))/2)

pics = ['biber1', 'biber2','biber3','biber4', 'biber5', 'biber6', 'biber7', 'biber8']

# %%
def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    pygame.mixer.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mouse_x = 0
    mouse_y = 0
    pygame.display.set_caption('Movie poster')
    pygame.display.set_icon(pygame.image.load('data\img\movie_icon.png'))
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # 첫 클릭 좌표 저장
    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)