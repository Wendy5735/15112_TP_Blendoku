from cmu_graphics import *
import random, math, shelve
from PIL import Image

# Image citations: 
# Khai, Tran. “Enter, circle, exit icon.” Iconfinder, www.iconfinder.com/icons/559770/enter_circle_exit_in_log_out_sign_icon
# Ranah Pixel Studio. “Hint, idea, tips icon.” Iconfinder, www.iconfinder.com/icons/4634593/hint_idea_tips_creative_ui_icon
# IconSrc. “Refresh, replay, restart icon.” Iconfinder, www.iconfinder.com/icons/5204369/refresh_replay_restart_icon
# Cherem, Ricardo. "Ask, doubt, faq icon." Iconfinder, www.iconfinder.com/icons/717640/ask_doubt_faq_hint_question_quiz_icon 
# Ionicons pack. “Play icon.” Iconfinder, www.iconfinder.com/icons/211876/play_icon
# Ionicons pack. Pause icon.” Iconfinder, www.iconfinder.com/icons/211871/pause_icon

#Citation: I was introduced to the "shelve" module from https://stackoverflow.com/questions/16726354/saving-the-highscore-for-a-game
# and then I did more research from https://python.fandom.com/wiki/Shelve
# d = shelve.open('Highest Score.txt')
# d['1'] = None
# d['2'] = None
# d['3'] = None
# d['4'] = None
# d['5'] = None
# d['6'] = None
# d['7'] = None
# d['8'] = None
# d.close()

class Level():
    def __init__(self,board,prefilledNum, levelNum):
        self.levelNum = levelNum
        self.board = board
        self.boardShape = self.findCellsInThisBoardShape()
        self.num = len(self.boardShape)
        self.prefilledNum = prefilledNum
        self.prefilledCell = self.selectPrefilledCell() # store the tuples of (row,col) of the cells that are prefilled
        self.solutionBoard = [[False] * 5 for i in range(5)]
        self.fillSolutionBoard()
        self.fillPrefilledCell()
        self.width = 400
        self.height = 800
        self.cellWidth = 50
        self.boardLeft = 75
        self.boardTop = 300
        self.waitingZoneRows = 2
        self.waitingZoneCols = math.ceil((self.num - self.prefilledNum)/2)
        self.waitingZoneTop = 50
        self.waitingZoneLeft = (self.width - self.waitingZoneCols * self.cellWidth)/2
        self.waitingZoneBoard = self.setWaitingZoneBoard()
        self.selectedCellBoard = None
        self.selectedCell = None

        self.moves = 0 # count how many moves the player make
        self.deciseconds = 0
        self.seconds = 0
        self.minutes = 0
        self.stepsPerSecond = 10
        self.previousClickTime = None
        self.previousClickLocation = None
        self.lockedCell = [] # store the tuples of (row,col) of the cells that are locked
    
        self.paused = False
        self.success = False

        self.exitButton = CMUImage(Image.open('Exit.png')) 
        self.restartButton = CMUImage(Image.open('Restart.png'))
        self.smartHintButton = CMUImage(Image.open('Smart Hint.png'))
        self.hintButton = CMUImage(Image.open('Hint.png'))
        self.hintButtonWidth = getImageSize(self.hintButton)[0]//70
        self.hintsRemained = 2
        self.hintClicked = False
        self.pauseButton = CMUImage(Image.open('Pause.png'))
        self.playButton = CMUImage(Image.open('Play.png'))

    def findCellsInThisBoardShape(self):
        boardShape = []
        for row in range(5):
            for col in range(5):
                if self.board[row][col] != False:
                    boardShape.append((row,col))
        return boardShape

    def fillSolutionBoard(self):
    # first loop through the board to find cell with 1 connection
        for (row,col) in self.boardShape:
            numOfNeighbor,direction = self.findCellNeighbor(row,col)
            if numOfNeighbor == 1:
                # get the entire line
                direction = direction[0]
                line = self.getLine(row,col,direction)
                # find the position of cell with colors
                coloredCells = self.getColoredCellInThisLine(line)
                if len(coloredCells) == len(line): # all line is filled
                    continue
                elif len(coloredCells) == 0: # none is filled
                    self.fillLineIf0IsFilled(line)
                elif len(coloredCells) == 1: # 1 cell in the line is filled
                    self.fillLineIf1IsFilled(line,coloredCells)
                elif len(coloredCells) == 2: # 2 cells in the line are filled
                    self.fillLineIf2IsFilled(line, coloredCells)
                # check completion
                if self.checkForAllFilled(): return 
        # after finished with all cell with 1 connection, find cells with 2 connections
        for (row,col) in self.boardShape:
            numOfNeighbor,directions = self.findCellNeighbor(row,col)
            # make sure it has 2 neighbors and that they are not in the same line, but in a corner
            if numOfNeighbor == 2 and directions[0][0] != directions[1][0] and directions[0][1] != directions[1][1]:
                #get the two lines
                for i in range(2):
                    direction = directions[i]
                    line = self.getLine(row,col,direction)
                    coloredCells = self.getColoredCellInThisLine(line)
                    if len(coloredCells) == len(line): # all line is filled
                        continue
                    elif len(coloredCells) == 0: # none is filled
                        self.fillLineIf0IsFilled(line)
                    elif len(coloredCells) == 1: # 1 cell in the line is filled
                        if coloredCells[0]==line[0]: #if the colored cell is the startcell of this line
                            startCell=line[0]
                            row,col = startCell
                            startRGB = self.solutionBoard[row][col]
                            endRGB = self.generateRandomRGB()
                            blocks = len(line)
                            stepRGB = self.findStepRGB(startRGB,endRGB,blocks)
                            self.fillLineColor(startCell,line,startRGB,stepRGB)
                        else: 
                            self.fillLineIf1IsFilled(line,coloredCells)
                    elif len(coloredCells) == 2: # 2 cells in the line are filled
                        self.fillLineIf2IsFilled(line, coloredCells)
                    # check completion
                    if self.checkForAllFilled(): return 
        # last case for "I" shaped case. Find the cell with 3 connections
        for (row,col) in self.boardShape:
            numOfNeighbor,directions = self.findCellNeighbor(row,col)
            if numOfNeighbor == 3:
                #get the three lines (only one line should be not completely filled)
                for i in range(3):
                    direction = directions[i]
                    line = self.getLine(row,col,direction)
                    coloredCells = self.getColoredCellInThisLine(line)
                    if len(coloredCells) == len(line): # all line is filled
                        continue
                    else: # start and end of the line should already have colors
                        self.fillLineIf2IsFilled(line, coloredCells)
                    # check completion
                    if self.checkForAllFilled(): return 

    def fillLineIf0IsFilled(self, line):
        startCell = line[0]
        startRGB, endRGB = self.generateRandomRGB(), self.generateRandomRGB()
        blocks = len(line)
        stepRGB = self.findStepRGB(startRGB,endRGB,blocks)
        self.fillLineColor(startCell,line,startRGB,stepRGB)
    
    def fillLineIf1IsFilled(self,line,coloredCells):
        startCell=line[0]
        startRGB = self.generateRandomRGB()
        row,col = coloredCells[0]
        endRGB = self.solutionBoard[row][col]
        coloredCellIndex = line.index(coloredCells[0])
        blocks = coloredCellIndex+1
        stepRGB = self.findStepRGB(startRGB,endRGB,blocks)
        self.fillLineColor(startCell,line,startRGB,stepRGB)

    def fillLineIf2IsFilled(self,line, coloredCells):
        startCell=coloredCells[0]
        row,col = startCell
        startRGB = self.solutionBoard[row][col]
        row,col = coloredCells[1]
        endRGB = self.solutionBoard[row][col]
        blocks = line.index(coloredCells[1]) - line.index(coloredCells[0]) + 1
        stepRGB = self.findStepRGB(startRGB,endRGB,blocks)
        self.fillLineColor(startCell,line,startRGB,stepRGB)

    def checkForAllFilled(self):
        for (row,col) in self.boardShape:
            if self.solutionBoard[row][col] == False:
                return False
        return True
    
    def fillLineColor(self,startCell,line,startRGB,stepRGB):
        index = line.index(startCell)
        left,right = index, index+1 # two pointers
        # fill the cells to the left of the startCell
        x = 0
        while 0<=left:
            row,col = line[left]
            rgb = []
            for i in range (3):
                component = startRGB[i] - stepRGB[i]*x
                if component < 0: component = 0
                elif component > 255: component = 255
                rgb.append(component)        
            self.solutionBoard[row][col] = rgb
            left -= 1
            x += 1
        # fill the cells to the right of the startCell
        x = 1
        while right<len(line):
            row,col = line[right]
            rgb = []
            for i in range (3):
                component = startRGB[i] + stepRGB[i]*x
                if component <0: component = 0
                elif component > 255: component = 255
                rgb.append(component)
            self.solutionBoard[row][col] = rgb
            right += 1
            x += 1

    def findStepRGB(self,startRGB,endRGB,blocks):
        stepRGB = [None] * 3
        for i in range(3):
            stepRGB[i] = (endRGB[i]-startRGB[i])/(blocks-1)
        return stepRGB

    def getColoredCellInThisLine(self,line):
        coloredCell = []
        for row,col in line:
            if self.solutionBoard[row][col] != False:
                coloredCell.append((row,col))
        return coloredCell

    def getLine(self,row,col,direction): # return a list of tuples that represent the position of each cell in the line
        line = []
        drow,dcol = direction
        while 0<=row<5 and 0<=col<5 and self.board[row][col] != False:
            line.append((row,col))
            row += drow
            col += dcol
        return line

    def findCellNeighbor(self,row,col):
        count = 0
        lineDirections = []
        for drow,dcol in ((-1,0),(0,-1),(1,0),(0,1)):
            nRow,nCol = row + drow, col + dcol
            if 0<=nRow<5 and 0<=nCol<5 and self.board[nRow][nCol] != False:
                count += 1
                lineDirections.append((drow,dcol))
        return count, lineDirections
    
    def generateRandomRGB(self):
        randomRGB = [None]*3
        for i in range(3):
            randomRGB[i] = random.randint(0,255)
        return randomRGB

    def selectPrefilledCell(self): # randomly select the cell positions according to the prefilled Number
        n = 0
        prefilledCell = []
        while n < self.prefilledNum:
            row,col = random.randint(0,4), random.randint(0,4)
            if self.board[row][col] != False and (row,col) not in prefilledCell:
                n+=1
                prefilledCell.append((row,col))
        return prefilledCell # return the positions of the prefilled cells

    def fillPrefilledCell(self): # fill the prefilled cells on the board
        for (row,col) in self.prefilledCell:
            self.board[row][col] = self.solutionBoard[row][col]
            
    def setWaitingZoneBoard(self): 
        shuffledColors = []
        # first find all the colors generated for this board except the prefilled colors
        for (row,col) in self.boardShape:
            if (row,col) not in self.prefilledCell:
                shuffledColors.append(self.solutionBoard[row][col])
        # shuffle the colors and place them in a 2D list with 2 rows (this will be the waiting zone)
        random.shuffle(shuffledColors)
        waitingZone = [[None] * self.waitingZoneCols for i in range(self.waitingZoneRows)]
        for row in range(self.waitingZoneRows):
            for col in range(self.waitingZoneCols):
                if col+row*self.waitingZoneCols < len(shuffledColors):
                    waitingZone[row][col] = shuffledColors[col+row*self.waitingZoneCols]
        return waitingZone

    # a function to test if my solution algorithm works
    def drawSolutionBoard(self):
        for (row,col) in self.boardShape:
            color = rgb(self.solutionBoard[row][col][0],self.solutionBoard[row][col][1],self.solutionBoard[row][col][2])
            self.drawCell(row, col,color,None)

    def drawBoard(self):
        for (row,col) in self.boardShape:
            self.drawEmptyCell(row,col)
            if self.board[row][col] != None: # check if it has color: then drawCell
                color = rgb(self.board[row][col][0],self.board[row][col][1],self.board[row][col][2])
                border = 'white' if (self.selectedCellBoard=='board' and self.selectedCell==(row,col)) else None
                self.drawCell(row, col, color, border)

    def drawWaitingZone(self):
        rows = self.waitingZoneRows
        cols = self.waitingZoneCols
        zoneLeft = self.waitingZoneLeft
        for row in range(rows):
            for col in range(cols):
                drawRect(zoneLeft+self.cellWidth*col+15, self.waitingZoneTop+self.cellWidth*row+15, 20,20,fill='gray') # draw empty waiting zone cell
                if self.waitingZoneBoard[row][col] != None:
                    color = rgb(self.waitingZoneBoard[row][col][0],self.waitingZoneBoard[row][col][1], self.waitingZoneBoard[row][col][2])
                    haveBorder = 'white' if (self.selectedCellBoard=='waitingZone' and self.selectedCell==(row,col)) else None # draw border if the cell is being selected
                    drawRect(zoneLeft+self.cellWidth*col, self.waitingZoneTop+self.cellWidth*row, self.cellWidth, self.cellWidth, fill = color, border = haveBorder)

    def drawCell(self, row, col, color, b):
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        drawRect(cellLeft, cellTop, self.cellWidth, self.cellWidth,
                fill=color, border=b)
        if (row,col) in self.prefilledCell and not self.success:
            self.drawCheck(cellLeft+35, cellTop+40)
        elif (row,col) in self.lockedCell and not self.success:
            self.drawLock(cellLeft+35, cellTop+32)
    
    def getCellLeftTop(self, row, col):
        cellLeft = self.boardLeft + col * self.cellWidth
        cellTop = self.boardTop + row * self.cellWidth
        return (cellLeft, cellTop)

    def drawCheck(self,x,y):
        drawPolygon(x, y, x+5, y+3, x+12, y-6, x+5, y+7, fill='black')

    def drawLock(self,x,y):
        drawOval(x, y, 8, 10, rotateAngle = -25, fill=None, border='black', borderWidth=2)
        drawRect(x+3, y+6, 12, 10, rotateAngle = -25, fill=None, border='black', borderWidth=4, align='center')
        drawRect(x-2, y+3, 3, 8, rotateAngle = -25, fill='black')
        drawRect(x+4, y, 3, 8, rotateAngle = -25, fill='black')

    def drawEmptyCell(self, row, col): # draw the four corners that wrap an empty cell
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        space = 4
        innerWidth = self.cellWidth - space*2
        length = 8
        drawLine(cellLeft+space, cellTop+space, cellLeft+space+length, cellTop+space,fill='gray')
        drawLine(cellLeft+space, cellTop+space, cellLeft+space, cellTop+space+length, fill='gray')
        drawLine(cellLeft+space+innerWidth, cellTop+space, cellLeft+space+innerWidth-length, cellTop+space, fill='gray')
        drawLine(cellLeft+space+innerWidth, cellTop+space, cellLeft+space+innerWidth, cellTop+space+length, fill='gray')
        drawLine(cellLeft+space, cellTop+space+innerWidth, cellLeft+space, cellTop+space+innerWidth-length, fill='gray')
        drawLine(cellLeft+space, cellTop+space+innerWidth, cellLeft+space+length, cellTop+space+innerWidth, fill='gray')
        drawLine(cellLeft+space+innerWidth, cellTop+space+innerWidth-length, cellLeft+space+innerWidth, cellTop+space+innerWidth, fill='gray')
        drawLine(cellLeft+space+innerWidth-length, cellTop+space+innerWidth, cellLeft+space+innerWidth, cellTop+space+innerWidth, fill='gray')

    # a helper function for the onMousePress to see if it is double-click
    def doubleClick(self,clickTime, clickLocation):
        return (self.previousClickTime != None and self.previousClickLocation != None
                and self.previousClickLocation == clickLocation and (clickTime - self.previousClickTime)<=2)

    # a helper function for the onMousePress to see which cell is clicked
    def getCell(self, x, y):
        # check if in waiting zone:
        dy = y - self.waitingZoneTop
        dx = x - self.waitingZoneLeft
        row = math.floor(dy/50)
        col = math.floor(dx/50)
        if 0<=row<self.waitingZoneRows and 0<=col<self.waitingZoneCols:
            return ('waitingZone', (row,col))
        else: # check if on board:
            dy = y - self.boardTop
            dx = x - self.boardLeft
            row = math.floor(dy/50)
            col = math.floor(dx/50)
            if 0<=row<5 and 0<=col<5 and self.board[row][col] != False:
                return ('board', (row,col))
            else:
                return (None,None)
    
    def giveHint(self):
        if self.hintsRemained > 0:
            while True:
                row,col = random.randint(0,4), random.randint(0,4)
                if self.board[row][col] == None:
                    self.hintsRemained -= 1
                    self.board[row][col] = self.solutionBoard[row][col]
                    break
    
    # given a color, find its position on the board or waiting zone
    def getColorLocation(self, rgb):
        for row in range(self.waitingZoneRows):
            for col in range(self.waitingZoneCols):
                if self.waitingZoneBoard[row][col] == rgb:
                    return ('waitingZone', (row,col))
        for (row,col) in self.boardShape:
            if self.board[row][col] == rgb:
                return ('board', (row,col))
    
    def findSmartHintCell(self):
        # smart hint will find the cell on the board with the 
        # largest number of incorrect/empty neighbors around it
        targetCell = None
        largestNum = 0
        for (row,col) in self.boardShape:
            count = 0
            for (drow,dcol) in [(1,0),(-1,0),(0,1),(0,-1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                rowN,colN = row+drow, col+dcol
                if ((rowN,colN) in self.boardShape and (rowN,colN) not in self.prefilledCell 
                and self.board[row][col] != self.solutionBoard[row][col]):
                    count += 1
            if count > largestNum:
                largestNum = count
                targetCell = (row,col)
        return targetCell

    def drawTimerAndSuccess(self):
        minutes = f'0{self.minutes}'if self.minutes<10 else f'{self.minutes}'
        seconds = f'0{self.seconds}'if self.seconds<10 else f'{self.seconds}'
        if not self.success:
            drawLabel(f'Moves: {self.moves}', self.width/2, self.height-90, fill='white',bold=True)
            drawLabel(f'{minutes}:{seconds}', self.width/2, self.height-75, fill='white',bold=True)
        else:
            drawLabel('Success!',self.width/2,120,size = 25,fill='white',bold=True)
            drawLabel(f'Time: {minutes}:{seconds} | Moves: {self.moves+(2-self.hintsRemained)}', self.width/2,75, size=16, fill='white')
            if self.levelNum != 8:
                d=shelve.open('Highest Score.txt')
                if d[str(self.levelNum+1)]!=None:
                    minutesH,secondsH,moves = d[str(self.levelNum+1)]
                    minutesH = f'0{minutesH}'if minutesH<10 else f'{minutesH}'
                    secondsH = f'0{secondsH}'if secondsH<10 else f'{secondsH}'
                    drawLabel(f'Best Time: {minutesH}:{secondsH} | Moves: {moves}', self.width/2,50, size=16, fill='white')

    def drawExitButton(self):
        imageWidth, imageHeight = getImageSize(self.exitButton)
        drawImage(self.exitButton, 40, self.height-50, align = 'center', width=imageWidth//75, height=imageHeight//75)

    def drawRestartButton(self):
        imageWidth, imageHeight = getImageSize(self.restartButton)
        drawImage(self.restartButton, self.width/2, self.height-50, align = 'center', width=imageWidth//70, height=imageHeight//70)

    def drawHintButton(self):
        drawImage(self.hintButton, self.width-40, self.height-50, align = 'center', width=self.hintButtonWidth, height=self.hintButtonWidth)
        drawLabel(self.hintsRemained, self.width-40, self.height-75, fill='white', bold=True)

    def drawSmartHintButton(self):
        imageWidth, imageHeight = getImageSize(self.smartHintButton)
        drawImage(self.smartHintButton, self.width-40, self.height-100, align = 'center', width=imageWidth//75, height=imageHeight//75)

    def drawPauseButton(self):
        imageWidth, imageHeight = getImageSize(self.pauseButton)
        drawImage(self.pauseButton, self.width-30, 30, align = 'center', width=imageWidth//75, height=imageHeight//75)

    def drawPlayButton(self):
        imageWidth, imageHeight = getImageSize(self.playButton)
        drawImage(self.playButton, self.width-30, 30, align = 'center', width=imageWidth//75, height=imageHeight//75)
