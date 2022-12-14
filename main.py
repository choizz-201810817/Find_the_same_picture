#%%
import random, pygame, sys, cx_Freeze
from PIL import Image
from pygame.locals import *
from multiprocessing import Queue

FPS = 30
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
REVEALSPEED = 8
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

pics = ['avatar', 'avengers','harrypotter','interstellar', 'jurassik', 'myeongnyang', 'spyderman', 'titanic']

# %%
def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    pygame.mixer.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mouse_x = 0
    mouse_y = 0
    pygame.display.set_caption('BTS ')
    pygame.display.set_icon(pygame.image.load('data\img\movie_icon.png'))
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    backImg = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\purple_back.png')

    firstSelection = None # 첫 클릭 좌표 저장
    DISPLAYSURF.blit(backImg, (0,0))
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False

        DISPLAYSURF.blit(backImg, (0,0))
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mouse_x, mouse_y)
        if boxx != None and boxy != None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True
                if firstSelection == None:
                    firstSelection = (boxx, boxy)
                else:
                    icon1shape, icon1color = getPicAndNum(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getPicAndNum(mainBoard, boxx, boxy)
                    if icon1shape != icon2shape or icon1color != icon2color:
                        # 둘이 다르면 모두 닫음
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False

                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(1000)

                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        startGameAnimation(mainBoard)
                        # pygame.mixer.music.play(-5,0.0)
                    firstSelection = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return False
    return True

def generateRevealedBoxesData(val): # 열린 상자 만들기
    revealedBoxes = []
    
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val]*BOARDHEIGHT)
    return revealedBoxes

def getRandomizedBoard(): # 카드 섞기
    global pics
    cards = []

    for pic in pics:
        for num in range(1,2):
            cards.append((pic,num))
    random.shuffle(cards)
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

def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i+groupSize])
    return result

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx*(BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy*(BOXSIZE + GAPSIZE) + YMARGIN

    return left, top

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawCard(pic, num, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)
    eight = int(BOXSIZE * 0.125)

    left, top = leftTopCoordsOfBox(boxx, boxy)

    pic1 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_avatar.png')
    pic2 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_avengers.png')
    pic3 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_harrypotter.png')
    pic4 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_interstellar.png')
    pic5 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_jurassik.png')
    pic6 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_myeongnyang.png')
    pic7 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_spyderman.png')
    pic8 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\poster_titanic.png')

    if pic == 'avatar':
        DISPLAYSURF.blit(pic1, (left, top))
    elif pic == 'avengers':
        DISPLAYSURF.blit(pic2, (left, top))
    elif pic == 'harrypotter':
        DISPLAYSURF.blit(pic3, (left, top))
    elif pic == 'interstellar':
        DISPLAYSURF.blit(pic4, (left, top))
    elif pic == 'jurassik':
        DISPLAYSURF.blit(pic5, (left, top))
    elif pic == 'myeongnyang':
        DISPLAYSURF.blit(pic6, (left, top))
    elif pic == 'spyderman':
        DISPLAYSURF.blit(pic7, (left, top))
    elif pic == 'titanic':
        DISPLAYSURF.blit(pic8, (left, top))

def getPicAndNum(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]

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

# 상자 열림
def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOXSIZE, (-REVEALSPEED) -1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)

# 상자 닫힘
def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF, BOXSIZE, (left, top, BOXSIZE, BOXSIZE))
            else:
                pic, num = getPicAndNum(board, boxx, boxy)
                drawCard(pic, num, boxx, boxy)

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxlist = random.sample(boxes, 4)
    boxGroups = splitIntoGroupsOf(1, boxlist)
    drawBoard(board, coveredBoxes)

    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
    coveredBoxes = generateRevealedBoxesData(True)
    global BOXSIZE
    w = 800
    h = 600
    size = (w, h)

    pic0 = pygame.image.load('C:\sbbigdata\Find_the_same_picture\data\img\stars.png')

    screen = pygame.display.set_mode(size)
    # color1 = LIGHTBGCOLOR
    # color2 = BGCOLOR

# %%
if __name__ == '__main__':
    main()
# %%
