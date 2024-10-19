from cmu_graphics import *
import copy, random, math
from PIL import Image

# Image citations: 
# Khai, Tran. “Enter, circle, exit icon.” Iconfinder, www.iconfinder.com/icons/559770/enter_circle_exit_in_log_out_sign_icon
# Ionicons pack. “Play icon.” Iconfinder, www.iconfinder.com/icons/211876/play_icon

class twoPlayerLevel():
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

        self.deciseconds = 0
        self.seconds = 0
        self.minutes = 0
        self.stepsPerSecond = 10
        self.previousClickTime = None
        self.previousClickLocation = None
        self.lockedCell = [] # store the tuples of (row,col) of the cells that are locked
    
        self.success = False

        self.exitButton = CMUImage(Image.open('Exit.png')) 

        self.player = 'player 1' # the current player 
        self.scores = [0,0] # [player1's score, player2's score]
        self.noMoves = False
        self.emptyCells = self.countEmptyCells()
        self.pointBoard = [[False] * 5 for i in range(5)]
        self.fillPointBoard()
        self.playerStartBoard = copy.deepcopy(self.board)

        self.playButton = CMUImage(Image.open('Play.png'))


    def findCellsInThisBoardShape(self):
        boardShape = []
        for row in range(5):
            for col in range(5):
                if self.board[row][col] != False:
                    boardShape.append((row,col))
        return boardShape

    def countEmptyCells(self):
        empty = []
        for row,col in self.boardShape:
            if self.board[row][col] == None:
                empty.append((row,col))
        return empty

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
        if self.pointBoard[row][col] != False:
            drawLabel(self.pointBoard[row][col], cellLeft+38, cellTop+35, size=16, fill='gray')

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

    def drawSuccessPlayer(self):
        if self.success:
            drawLabel('Success!',self.width/2,120,size = 25,fill='white',bold=True)
            drawLabel(f'{self.scores[0]}|{self.scores[1]}', self.width/2, 50, size=16, fill='white')
            if self.scores[0]==self.scores[1]: #tie
                drawLabel(f'Tied', self.width/2, 80, size=18, fill='white')
            else:
                winner = 'player 1' if self.scores[0]>self.scores[1] else 'player 2'
                drawLabel(f'Winner: {winner}', self.width/2, 80, size=18, fill='white')
    
    def drawExitButton(self):
        imageWidth, imageHeight = getImageSize(self.exitButton)
        drawImage(self.exitButton, 40, self.height-50, align = 'center', width=imageWidth//75, height=imageHeight//75)

    def drawPlayersScore(self):
        color = 'white' if self.player == 'player 1' else rgb(55,55,100)
        drawRoundedRect(self.width/2-80, self.height-75, 90,40, color)
        highlight = True if self.player == 'player 1' else False
        color = 'black' if self.player == 'player 1' else 'white'
        drawLabel(f'player 1', self.width/2-80, self.height-75, align='center',fill=color, size=18, bold=highlight)
        
        color = 'white' if self.player == 'player 2' else rgb(55,55,100)
        drawRoundedRect(self.width/2+80, self.height-75, 90,40, color)
        highlight = True if self.player == 'player 2' else False
        color = 'black' if self.player == 'player 2' else 'white'
        drawLabel(f'player 2', self.width/2+80, self.height-75, align='center',fill=color, size=18, bold=highlight)
        
        if self.noMoves == True: # draw the button to let player submit his/her answer
            drawRoundedRect(self.width/2, self.height-75, 50,40, 'green')
            imageWidth, imageHeight = getImageSize(self.playButton)
            drawImage(self.playButton, self.width/2, self.height-75, align = 'center', width=imageWidth//75, height=imageHeight//75)
        else: # draw the scores
            drawRoundedRect(self.width/2, self.height-75, 50,40, 'white')
            drawLabel(f'{self.scores[0]}|{self.scores[1]}',self.width/2, self.height-75,size=18)

    def changeTurn(self):
        self.player = 'player 2' if self.player=='player 1' else 'player 1'
        self.noMoves = False # replenish the 2 available moves for next player
        self.emptyCells = self.countEmptyCells()
        self.playerStartBoard = copy.deepcopy(self.board) # update the startBoard for the next player

    # create a 2D list that store the points of every empty cell
    # main: a cell's up, down, left, right's neighbors
    # secondary: a cell's upup, downdown, leftleft, rightright's neighbors
    # corner: a cell's up-left, up-right, down-left, down-right's neighbors
    # if main is filled: point = 1;
    # if secondary or corner is filled: point = 2;
    # if none is filled: point = 3
    def fillPointBoard(self):
        for (row,col) in self.boardShape:
            mainCount = 0 # count the cell's up, down, left, right's neighbors that are filled
            secondaryCount = 0 # count the cell's upup, downdown, leftleft, rightright's neighbors that are filled
            cornerCount = 0 # count the cell's up-left, up-right, down-left, down-right's neighbors that are filled
            for (drow,dcol) in [(1,0),(-1,0),(0,1),(0,-1)]:
                rowN,colN = row+drow, col+dcol
                if (rowN,colN) in self.boardShape and (rowN,colN) in self.prefilledCell:
                    mainCount += 1
                elif (rowN,colN) in self.boardShape and (rowN+drow,colN+dcol) in self.prefilledCell:
                    secondaryCount += 1
            for (drow,dcol) in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                rowN,colN = row+drow, col+dcol
                if (rowN,colN) in self.boardShape and (rowN,colN) in self.prefilledCell:
                    cornerCount += 1
            if mainCount >= 1:
                self.pointBoard[row][col] = 1
            elif cornerCount >= 1 or secondaryCount >= 1:
                self.pointBoard[row][col] = 2
            else:
                self.pointBoard[row][col] = 3

    # give the cells that are placed by this player
    def getPlacedCells(self, playerStartBoard, playerEndBoard):
        cells = []
        for (row,col) in self.boardShape:
            if playerStartBoard[row][col] != playerEndBoard[row][col]:
                cells.append((row,col))
        return cells

    def checkCorrectness(self,cells):
        points = 0
        for (row,col) in cells:
            if self.board[row][col] == self.solutionBoard[row][col]:
                self.prefilledCell.append((row,col))
                points += self.pointBoard[row][col]
            else: # if incorrectly filled, place this color back to the waiting zone
                for rowW in range(self.waitingZoneRows):
                    for colW in range(self.waitingZoneCols):
                        if self.waitingZoneBoard[rowW][colW] == None:
                            self.waitingZoneBoard[rowW][colW],self.board[row][col] = self.board[row][col],self.waitingZoneBoard[rowW][colW]
        return points

    def updatePoints(self,points):
        if self.player == 'player 1': 
            self.scores[0] += points
        else:
            self.scores[1] += points

# ---------------------------------------------------
# a function written to enhance the UI
def drawRoundedRect(cX,cY,w,h,color):
    margin = 10
    innerW = w-margin*2
    innerH = h-margin*2
    drawRect(cX,cY,innerW+2,innerH+2,align='center',fill=color)
    drawCircle(cX-innerW/2,cY-innerH/2,margin,fill=color)
    drawCircle(cX+innerW/2,cY-innerH/2,margin,fill=color)
    drawCircle(cX-innerW/2,cY+innerH/2,margin,fill=color)
    drawCircle(cX+innerW/2,cY+innerH/2,margin,fill=color)
    drawRect(cX,cY-(innerH/2+margin/2),innerW,margin,align='center',fill=color)
    drawRect(cX,cY+(innerH/2+margin/2),innerW,margin,align='center',fill=color)
    drawRect(cX-(innerW/2+margin/2),cY,margin,innerH,align='center',fill=color)
    drawRect(cX+(innerW/2+margin/2),cY,margin,innerH,align='center',fill=color)

def multiPlayerGame_onMousePress(app, mouseX, mouseY):
    #check if click on Exit Button
    exitButtonX, exitButtonY = 40, app.level.height-50
    imageWidth, imageHeight = getImageSize(app.level.exitButton)
    width = imageWidth//75
    if exitButtonX-width/2 <= mouseX <= exitButtonX+width/2 and exitButtonY-width/2 <= mouseY <= exitButtonY+width/2:
        setActiveScreen('home')

    # other actions
    elif not app.level.success:
        clickTime = (60*app.level.minutes + app.level.seconds)*10 + app.level.deciseconds
        clickLocation = mouseX,mouseY
        board, cell = app.level.getCell(mouseX, mouseY)
        if cell != None:
            row,col = cell
            # check if it is double-click
            if board == 'board' and app.level.doubleClick(clickTime, clickLocation):
                if (row,col) not in app.level.lockedCell:
                    app.level.lockedCell.append((row,col))
                else:
                    app.level.lockedCell.remove((row,col))
                app.level.selectedCellBoard, app.level.selectedCell = None, None
                app.level.previousClickTime = None
                app.level.previousClickLocation = None

            elif board != 'board' or (row,col) not in app.level.prefilledCell: # if not click into the board or the row/col of the board is not in prefilled
                if board == app.level.selectedCellBoard and cell==app.level.selectedCell: # 1. if select the selected cell, unselect
                    app.level.selectedCellBoard, app.level.selectedCell = None, None
                elif app.level.selectedCell == None: # 2. if no current selection, select this cell
                    if board == 'waitingZone' and app.level.waitingZoneBoard[row][col] != None:
                        app.level.selectedCellBoard = 'waitingZone'
                        app.level.selectedCell = (row,col)
                    elif board == 'board' and app.level.board[row][col] != None:
                        app.level.selectedCellBoard = 'board'
                        app.level.selectedCell = (row,col)
                else: # 3. else, swap the two cells
                    selectedRow,selectedCol = app.level.selectedCell
                    if (board=='board' and (row,col) in app.level.lockedCell) or (app.level.selectedCellBoard=='board' and (selectedRow,selectedCol) in app.level.lockedCell):
                        return # if one of the two cells is locked, don't swap
                    if app.level.selectedCellBoard == 'waitingZone' and board=='waitingZone':
                        app.level.waitingZoneBoard[selectedRow][selectedCol], app.level.waitingZoneBoard[row][col] = app.level.waitingZoneBoard[row][col], app.level.waitingZoneBoard[selectedRow][selectedCol]
                    elif app.level.selectedCellBoard == 'board' and board=='waitingZone':
                        app.level.board[selectedRow][selectedCol], app.level.waitingZoneBoard[row][col] = app.level.waitingZoneBoard[row][col], app.level.board[selectedRow][selectedCol]
                    elif app.level.selectedCellBoard == 'waitingZone' and board=='board':
                        # check if there is still moves, or if there is no moves but the action is just swapping colors
                        if not app.level.noMoves or (app.level.noMoves and app.level.board[row][col] != None):
                            app.level.waitingZoneBoard[selectedRow][selectedCol], app.level.board[row][col] = app.level.board[row][col], app.level.waitingZoneBoard[selectedRow][selectedCol]
                    elif app.level.selectedCellBoard == 'board' and board=='board':
                        app.level.board[selectedRow][selectedCol], app.level.board[row][col] = app.level.board[row][col], app.level.board[selectedRow][selectedCol]
                    app.level.selectedCellBoard, app.level.selectedCell = None, None
            app.level.previousClickTime = clickTime
            app.level.previousClickLocation = clickLocation

        emptyCellsNow = app.level.countEmptyCells()
        if len(emptyCellsNow) == 0:
            # check if success
            if app.level.board == app.level.solutionBoard:
                app.level.success = True
                cells = app.level.getPlacedCells(app.level.playerStartBoard, app.level.board)
                points = app.level.checkCorrectness(cells)
                app.level.updatePoints(points)
        # if current player has placed 2 colors on the board:
        if len(app.level.emptyCells)-len(emptyCellsNow) == 2:
            app.level.noMoves = True
        else:
            app.level.noMoves = False

    # check if click on green confirm button
    if app.level.noMoves and not app.level.success: 
        greenButtonCX = app.level.width/2
        greenButtonCY = app.level.height-75
        if greenButtonCX-25 <= mouseX <= greenButtonCX+25 and greenButtonCY-20 <= mouseY <= greenButtonCY+20:
            # check if success
            if app.level.board == app.level.solutionBoard:
                app.level.success = True
                cells = app.level.getPlacedCells(app.level.playerStartBoard, app.level.board)
                points = app.level.checkCorrectness(cells)
                app.level.updatePoints(points)
            else:
                cells = app.level.getPlacedCells(app.level.playerStartBoard, app.level.board)
                points = app.level.checkCorrectness(cells)
                app.level.updatePoints(points)
                app.level.fillPointBoard() # update the point board based on updated filled board
                app.level.changeTurn()

def multiPlayerGame_onStep(app):
    if not app.level.success:
        app.level.deciseconds += 1
        if app.level.deciseconds>10:
            app.level.seconds += 1
            app.level.deciseconds = 0
        if app.level.seconds>60:
            app.level.minutes += 1
            app.level.seconds = 0

def multiPlayerGame_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    app.level.drawBoard()
    if not app.level.success:
        app.level.drawWaitingZone()
    app.level.drawExitButton()
    app.level.drawSuccessPlayer()
    app.level.drawPlayersScore()
    drawLabel(f'Level {app.currentLevel+1}', 45, 25, fill='white', bold=True, size=15)