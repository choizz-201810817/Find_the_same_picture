#%%
import random, pygame, sys, cx_Freeze
from PIL import Image
from pygame.locals import *
from multiprocessing import Queue
import time

FPS = 30
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
REVEALSPEED = 10
BOXSIZE = 100
GAPSIZE = 10
BOARDWIDTH = 4
BOARDHEIGHT = 4
BGCOLOR = (173,114,254)
BOXCOLOR = (43, 17, 142)
HIGHLIGHTCOLOR = (255,255,255)

assert (BOARDWIDTH * BOARDWIDTH) % 2 == 0, '이미지 개수가 짝수'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE)))/2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE)))/2)

pics = ['bts', 'rm', 'jin', 'suga', 'jhope', 'jimin', 'v', 'jk']


#%%

class Button:  # 버튼
    def __init__(self, img_in, x, y, width, height, img_act, x_act, y_act, action=None):
        mouse = pygame.mouse.get_pos()  # 마우스 좌표
        click = pygame.mouse.get_pressed()  # 클릭여부
        if x + width > mouse[0] > x and y + height > mouse[1] > y:  # 마우스가 버튼안에 있을 때
            DISPLAYSURF.blit(img_act, (x_act, y_act))  # 버튼 이미지 변경
            if click[0] and action is not None:  # 마우스가 버튼안에서 클릭되었을 때
                time.sleep(0.2)
                action()
        else:
            DISPLAYSURF.blit(img_in, (x, y))
            
def mainmenu():
    global BOARDWIDTH, BOARDHEIGHT, FPSCLOCK, DISPLAYSURF
    FPSCLOCK = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    
    pygame.display.set_caption('BTS MATCH GAME')
    pygame.display.set_icon(pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts_logo.png'))
    
    backImg = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\purple_back.png')
    main_pic = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\main_img.png')
    mainmenu_start = pygame.image.load(r"C:\sbbigdata\Find_the_same_picture\data\img\start.png")
    mainmenu_finish = pygame.image.load(r"C:\sbbigdata\Find_the_same_picture\data\img\finish.png")
    mainmenu_start_click = pygame.image.load(r"C:\sbbigdata\Find_the_same_picture\data\img\start_click.png")
    mainmenu_finish_click = pygame.image.load(r"C:\sbbigdata\Find_the_same_picture\data\img\finish_click.png")
    
    menu = True

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        DISPLAYSURF.blit(backImg, (0, 0))
        DISPLAYSURF.blit(main_pic, (105, 50))
        Button(mainmenu_start, 320, 370, 150, 80, mainmenu_start_click, 300, 355, main)
        Button(mainmenu_finish, 320, 450, 150, 80, mainmenu_finish_click, 300, 435, finishgame)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def main():
    global FPSCLOCK, DISPLAYSURF, BOARDWIDTH, BOARDHEIGHT
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(r"C:\sbbigdata\Find_the_same_picture\data\fire.wav")
    pygame.mixer.music.play(-5,0.0)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    font = pygame.font.Font(None, 40)
    

    mouse_x = 0
    mouse_y = 0
    # pygame.display.set_caption('BTS MATCH GAME')
    # pygame.display.set_icon(pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts_logo.png'))
    mainBoard = getRandomizedBoard() # 8개의 사진이름들을 불러와 각 사진들을 두 개씩 만들고, 이를 섞어서 4x4 리스트를 만듦
    revealedBoxes = generateRevealedBoxesData(False) # False(닫힌 형태)로 채워진 4x4 리스트 생성

    backImg = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\purple_back.png')

    firstSelection = None # 두 번의 클릭 중에 첫 클릭 좌표 저장하는 변수
    DISPLAYSURF.blit(backImg, (0,0))
    startGameAnimation(mainBoard)

    while True:
        ticks = pygame.time.get_ticks()
        millis=ticks%1000
        seconds=int(ticks/1000 % 60)
        minutes=int(ticks/60000 % 24)
        out='{0} : {1}'.format(minutes, seconds)
        timer = font.render(out, True, (255,255,255))
        
        mouseClicked = False

        DISPLAYSURF.blit(backImg, (0,0)) # 베걍화면 설정
        drawBoard(mainBoard, revealedBoxes) # 4x4 의 자리에 각각의 사진을 배치함

        DISPLAYSURF.blit(timer, (((WINDOWWIDTH/2) - 30), 10))
        pygame.display.flip()

        for event in pygame.event.get(): # 마우스 / 키보드 입력을 받음
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION: # 마우스 위치 이동
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONDOWN: # 마우스 클릭
                mouse_x, mouse_y = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mouse_x, mouse_y) # 마우스 좌표에 해당하는 박스 인덱스 가져오기
        if boxx != None and boxy != None: # (boxx, boxy)의 값이 존재(마우스 위치에 해당하는 상자가 있는 경우)
            if not revealedBoxes[boxx][boxy]: # 마우스 갖다 댄 상자에 하이라이트 생성
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked: # 마우스 위치의 박스를 눌렀을 때
                revealBoxesAnimation(mainBoard, [(boxx, boxy)]) # 마우스가 누른 박스의 커버 열기
                revealedBoxes[boxx][boxy] = True # 해당 박스 커버가 열려있다고 표시
                if firstSelection == None: # 처음 클릭이 진행되지 않은 경우
                    firstSelection = (boxx, boxy) # 클릭된 상자 위치 저장
                else: # 처음 클릭된 상자가 있는 경우
                    icon1shape, icon1color = getPicAndNum(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getPicAndNum(mainBoard, boxx, boxy)
                    if icon1shape != icon2shape or icon1color != icon2color: # 클릭된 두 상자가 다르다면..
                        # 둘이 다르면 모두 닫음
                        pygame.time.wait(800)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)]) # 처음 선택 상자와 두번째 선택 상자의 커버를 닫음
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                        # 두 상자 모두 닫힌 상태로 돌아감..

                    # 게임에서 이긴 경우
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(1000)

                        # 상자들을 다시 섞고 전체가 닫힌 상자 리스트를 다시 만듦.
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        DISPLAYSURF.blit(backImg, (0,0))
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        startGameAnimation(mainBoard)
                        # pygame.mixer.music.play(-5,0.0)
                        DISPLAYSURF.blit(timer, (((WINDOWWIDTH/2) - 30), 10))
                        pygame.display.flip()

                    firstSelection = None


        pygame.display.update()
        FPSCLOCK.tick(FPS)

# 상자들이 모두 열린 경우 -> 승리!!
def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i: # 하나라도 닫혀있으면 False반환
            return False
    return True

def generateRevealedBoxesData(val): # 열리거나 닫힌(val에 따라 달라짐) 상자 리스트 만들기
    revealedBoxes = []
    
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val]*BOARDHEIGHT)
    return revealedBoxes

def getRandomizedBoard(): # 카드 섞기
    global pics
    cards = []

    for pic in pics:
        for num in range(1,2):
            cards.append((pic,num)) # (사진이름, 1), (사진이름, 2) 이런 형태로 각 사진과 번호를 튜플로 묶어 같은 사진을 두 개씩 card 리스트에 넣음
    random.shuffle(cards) # 카드 섞기
    numCardsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)
    cards = cards[:numCardsUsed]*2
    random.shuffle(cards)

    board = []

    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(cards[0])
            del cards[0]
        board.append(column)

    return board

# 상자list의 요소들을 groupSize씩 또 list로 묶어 2차원이 되도록 함
def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i+groupSize])
    return result

def leftTopCoordsOfBox(boxx, boxy): # boxx, boxy는 각각 0~3사이의 값이 들어감
    # 해당 박스의 왼쪽상단의 좌표를 가져옴
    left = boxx*(BOXSIZE + GAPSIZE) + XMARGIN 
    top = boxy*(BOXSIZE + GAPSIZE) + YMARGIN
    return left, top

def getBoxAtPixel(x, y): # x, y는 마우스 클릭 좌표
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y): # 클릭 좌표가 박스 안에 있으면 True 아니면 False 반환
                return (boxx, boxy) # 16개의 상자중 클릭좌표에 해당하는 상자가 있으면 그 상자의 인덱스 반환
    return (None, None) # 해당하는 상자가 없는 경우 None을 반환


# pic에 해당하는 사진을 boxx, boxy 자리에 배치
def drawCard(pic, num, boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)

    pic1 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts1.jpg')
    pic2 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts2.jpg')
    pic3 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts3.jpg')
    pic4 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts4.jpg')
    pic5 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts5.jpg')
    pic6 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts6.jpg')
    pic7 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts7.jpg')
    pic8 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\bts8.jpg')

    if pic == 'bts':
        DISPLAYSURF.blit(pic1, (left, top))
    elif pic == 'rm':
        DISPLAYSURF.blit(pic2, (left, top))
    elif pic == 'jin':
        DISPLAYSURF.blit(pic3, (left, top))
    elif pic == 'suga':
        DISPLAYSURF.blit(pic4, (left, top))
    elif pic == 'jhope':
        DISPLAYSURF.blit(pic5, (left, top))
    elif pic == 'jimin':
        DISPLAYSURF.blit(pic6, (left, top))
    elif pic == 'v':
        DISPLAYSURF.blit(pic7, (left, top))
    elif pic == 'jk':
        DISPLAYSURF.blit(pic8, (left, top))

def getPicAndNum(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]

# 해당 상자의 위치에 점점 커지거나 작아지는 사각형(Rect)을 그려 덮개를 여닫음
def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        pic, num = getPicAndNum(board, box[0], box[1])
        drawCard(pic, num, box[0], box[1])

        if coverage > 0:
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))

    pygame.display.update()
    FPSCLOCK.tick(FPS)

# 박스 덮개 열림
# 박스의 오른쪽 끝에서부터 REVEALSPEED만큼씩 덮개가 줄어들어 열리게 됨
def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOXSIZE, -1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)

# 상자 닫힘
# 박스의 왼쪽 끝에서부터 BOXSIZE까지 REVEALSPEED로 덮개가 생겨 덮히게 됨
def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOXSIZE + 1, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]: # 해당 박스의 커버가 열려있으면..(False가 아니면)
                pygame.draw.rect(DISPLAYSURF, BOXSIZE, (left, top, BOXSIZE, BOXSIZE))
            else: # 해당 박스의 커버가 닫혀 있으면..(False라면)
                pic, num = getPicAndNum(board, boxx, boxy) # 튜플형태의 사진, 번호를 추출
                drawCard(pic, num, boxx, boxy) # (boxx, boxy)자리에 pic에 해당하는 사진을 배치

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
    coveredBoxes = generateRevealedBoxesData(False)

    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y)) # (0,0)~(4,4)
    random.shuffle(boxes)
    boxlist = random.sample(boxes, 4) # 게임 시작 전 보여줄 4개의 상자 랜덤하게 선택(힌트)
    boxGroups = splitIntoGroupsOf(1, boxlist) # 선정된 상자list의 요소 하나하나를 또 list로 묶어 2차원으로 만듦.
                                              # 아래 for문안의 함수들에 전달되는 인자(인수)들은 list형태가 되어야하기 때문
    drawBoard(board, coveredBoxes)

    # 선정된 4개의 상자들을 순서대로 보여줬다가 숨김
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

# 게임에서 이겼을 때..
def gameWonAnimation(board):
    coveredBoxes = generateRevealedBoxesData(True)
    global BOXSIZE
    w = 800
    h = 600
    size = (w, h)

    pic0 = pygame.image.load(r'C:\sbbigdata\Find_the_same_picture\data\img\stars.png')


    # screen = pygame.display.set_mode(size)
    # color1 = LIGHTBGCOLOR
    # color2 = BGCOLOR

def finishgame():
    pygame.quit()
    sys.exit()

# %%
if __name__ == '__main__':
    mainmenu()
# %%
