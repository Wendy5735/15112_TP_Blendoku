from cmu_graphics import *
import math, copy, shelve
from PIL import Image
from levelClass import *
from Multiplayer import *

# Image citations: 
# Khai, Tran. “Enter, circle, exit icon.” Iconfinder, www.iconfinder.com/icons/559770/enter_circle_exit_in_log_out_sign_icon
# Ranah Pixel Studio. “Hint, idea, tips icon.” Iconfinder, www.iconfinder.com/icons/4634593/hint_idea_tips_creative_ui_icon
# IconSrc. “Refresh, replay, restart icon.” Iconfinder, www.iconfinder.com/icons/5204369/refresh_replay_restart_icon
# Cherem, Ricardo. "Ask, doubt, faq icon." Iconfinder, www.iconfinder.com/icons/717640/ask_doubt_faq_hint_question_quiz_icon 
# Ionicons pack. “Play icon.” Iconfinder, www.iconfinder.com/icons/211876/play_icon
# Ionicons pack. Pause icon.” Iconfinder, www.iconfinder.com/icons/211871/pause_icon
# AbtoCreative. "Team, two player mode, co-op icon." Iconfinder, www.iconfinder.com/icons/10446061/team_two_player_mode_co-op_cooperative_teammate_multiplayer_icon


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

def loadBoardLevel(app):
    # each level = [board shape, prefilled cell number]
    level1 = ([[False, False, None, False, False],
              [False, False, None, False, False],
              [False, False, None, False, False],
              [False, False, None, False, False],
              [False, False, None, False, False]], 1) 
    level2 = ([[False, None, None, None, False],
              [False, False, False, None, False],
              [False, False, False, None, False],
              [False, False, False, None, False],
              [False, False, False, None, False]], 1)
    level3 = ([[None, None, None, None, None],
              [None, False, False, False, None],
              [None, False, False, False, None],
              [None, False, False, False, None],
              [False, False, False, False, None]], 2)
    level4 = ([[False, False, False, None, False],
              [False, None, None, None, None],
              [False, False, False, None, False],
              [False, False, False, None, False],
              [False, False, False, None, False]], 2)
    level5 = ([[False, None, None, None, None],
              [False, False, False, None, False],
              [False, False, False, None, False],
              [None, None, None, None, False],
              [False, False, False, False, False]], 2)
    level6 = ([[False, None, None, None, False],
              [False, False, False, None, False],
              [None, None, None, None, None],
              [None, False, False, None, False],
              [None, False, False, False, False]], 2)
    level7 = ([[None, None, None, None, None],
              [None, False, False, False, None],
              [None, False, False, False, None],
              [None, False, False, False, None],
              [None, None, None, None, None]], 3)
    level8 = ([[False, None, False, None, False],
              [None, None, None, None, None],
              [False, None, False, None, False],
              [False, None, False, None, False],
              [None, None, None, None, None]], 3)
    app.boardLevels = [level1,level2,level3,level4,level5,level6,level7,level8]

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

def onAppStart(app):
    app.currentLevel = None # an integer (1 less than the actual level)
    app.level = None # an instance of the class Level
    app.stepsPerSecond = 10
    app.exitButton = CMUImage(Image.open('Exit.png'))
    app.restartButton = CMUImage(Image.open('Restart.png'))
    app.hintButton = CMUImage(Image.open('Hint.png'))
    app.smartHintButton = CMUImage(Image.open('Smart Hint.png'))
    app.pauseButton = CMUImage(Image.open('Pause.png'))
    app.multiPlayerButton = CMUImage(Image.open('Multiplayer.png'))
    app.singlePlayerButton = CMUImage(Image.open('Singleplayer.png'))

    app.multiplayerMode = False

def restart(app):
    loadBoardLevel(app)
    board, prefilledNum = app.boardLevels[app.currentLevel]
    app.level = Level(board, prefilledNum,app.currentLevel)

def game_onMousePress(app, mouseX, mouseY):
    #check if click on pause
    pauseButtonX, pauseButtonY = app.level.width-30, 30
    imageWidth, imageHeight = getImageSize(app.level.pauseButton)
    width = imageWidth//75
    if pauseButtonX-width/2 <= mouseX <= pauseButtonX+width/2 and pauseButtonY-width/2 <= mouseY <= pauseButtonY+width/2:
        app.level.paused = not app.level.paused

    #check if click on Exit Button
    exitButtonX, exitButtonY = 40, app.level.height-50
    imageWidth, imageHeight = getImageSize(app.level.exitButton)
    width = imageWidth//75
    if exitButtonX-width/2 <= mouseX <= exitButtonX+width/2 and exitButtonY-width/2 <= mouseY <= exitButtonY+width/2:
        setActiveScreen('home')

    #check if click on Restart Button
    restartButtonX, restartButtonY = app.level.width/2, app.level.height-50
    imageWidth, imageHeight = getImageSize(app.level.restartButton)
    width = imageWidth//70
    if restartButtonX-width/2 <= mouseX <= restartButtonX+width/2 and restartButtonY-width/2 <= mouseY <= restartButtonY+width/2:
        if app.currentLevel == 8: # special case for level 9
            app.board9 = copy.deepcopy(app.board9Empty)
            app.level = Level(app.board9, app.level9PrefilledNum, 8)
        else:
            restart(app)

    #check if click on Hint Button
    if not app.level.paused:
        hintButtonX, hintButtonY = app.level.width-40, app.level.height-50
        width = app.level.hintButtonWidth
        if hintButtonX-width/2 <= mouseX <= hintButtonX+width/2 and hintButtonY-width/2 <= mouseY <= hintButtonY+width/2:
            if app.level.hintsRemained > 0:
                if app.level.hintClicked:
                    app.level.hintButtonWidth -= 10
                    app.level.hintClicked = False
                else:
                    app.level.hintButtonWidth += 10 # enlarge the button when clicked
                    app.level.hintClicked = True
    
    # Check if click on smart hint
    if not app.level.paused and not app.level.success:
        smartHintButtonX, smartHintButtonY = app.level.width-40, app.level.height-100
        imageWidth, imageHeight = getImageSize(app.level.smartHintButton)
        width = imageWidth//75
        if smartHintButtonX-width/2 <= mouseX <= smartHintButtonX+width/2 and smartHintButtonY-width/2 <= mouseY <= smartHintButtonY+width/2:
            if app.level.hintsRemained > 0:
                row,col = app.level.findSmartHintCell()
                correctColor = app.level.solutionBoard[row][col]
                correctColorBoard, correctColorLocation = app.level.getColorLocation(correctColor)
                correctColorRow, correctColorCol = correctColorLocation
                if correctColorBoard == 'board':
                    app.level.board[row][col], app.level.board[correctColorRow][correctColorCol] = app.level.board[correctColorRow][correctColorCol], app.level.board[row][col]
                else:
                    app.level.board[row][col], app.level.waitingZoneBoard[correctColorRow][correctColorCol] = app.level.waitingZoneBoard[correctColorRow][correctColorCol], app.level.board[row][col]
                app.level.hintsRemained -= 1
                # add the cell filled by the hint to the prefilled cell list
                app.level.prefilledCell.append((row,col)) 

    # Normal hint process
    if app.level.hintClicked and not app.level.paused and not app.level.success:
        board, cell = app.level.getCell(mouseX, mouseY)
        # check if click onto a valid cell on the board
        if board == 'board' and cell not in app.level.lockedCell and cell not in app.level.prefilledCell:
            row,col = cell
            correctColor = app.level.solutionBoard[row][col]
            correctColorBoard, correctColorLocation = app.level.getColorLocation(correctColor)
            correctColorRow, correctColorCol = correctColorLocation
            if correctColorBoard == 'board':
                app.level.board[row][col], app.level.board[correctColorRow][correctColorCol] = app.level.board[correctColorRow][correctColorCol], app.level.board[row][col]
            else:
                app.level.board[row][col], app.level.waitingZoneBoard[correctColorRow][correctColorCol] = app.level.waitingZoneBoard[correctColorRow][correctColorCol], app.level.board[row][col]
            app.level.hintsRemained -= 1
            app.level.hintButtonWidth -= 10
            app.level.hintClicked = False
            # add the cell filled by the hint to the prefilled cell list
            app.level.prefilledCell.append((row,col)) 
            
    # other actions
    elif not app.level.paused and not app.level.success:
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

            # if not click into the board or the row/col of the board is not in prefilled
            elif board != 'board' or (row,col) not in app.level.prefilledCell: 
                # 1. if select the selected cell, unselect
                if board == app.level.selectedCellBoard and cell==app.level.selectedCell: 
                    app.level.selectedCellBoard, app.level.selectedCell = None, None
                # 2. if no current selection, select this cell
                elif app.level.selectedCell == None: 
                    if board == 'waitingZone' and app.level.waitingZoneBoard[row][col] != None:
                        app.level.selectedCellBoard = 'waitingZone'
                        app.level.selectedCell = (row,col)
                    elif board == 'board' and app.level.board[row][col] != None:
                        app.level.selectedCellBoard = 'board'
                        app.level.selectedCell = (row,col)
                # 3. else, swap the two cells
                else: 
                    selectedRow,selectedCol = app.level.selectedCell
                    if (board=='board' and (row,col) in app.level.lockedCell) or (app.level.selectedCellBoard=='board' and (selectedRow,selectedCol) in app.level.lockedCell):
                        return # if one of the two cells is locked, don't swap
                    if app.level.selectedCellBoard == 'waitingZone' and board=='waitingZone':
                        app.level.waitingZoneBoard[selectedRow][selectedCol], app.level.waitingZoneBoard[row][col] = app.level.waitingZoneBoard[row][col], app.level.waitingZoneBoard[selectedRow][selectedCol]
                    elif app.level.selectedCellBoard == 'board' and board=='waitingZone':
                        app.level.board[selectedRow][selectedCol], app.level.waitingZoneBoard[row][col] = app.level.waitingZoneBoard[row][col], app.level.board[selectedRow][selectedCol]
                    elif app.level.selectedCellBoard == 'waitingZone' and board=='board':
                        app.level.waitingZoneBoard[selectedRow][selectedCol], app.level.board[row][col] = app.level.board[row][col], app.level.waitingZoneBoard[selectedRow][selectedCol]
                    elif app.level.selectedCellBoard == 'board' and board=='board':
                        app.level.board[selectedRow][selectedCol], app.level.board[row][col] = app.level.board[row][col], app.level.board[selectedRow][selectedCol]
                    app.level.selectedCellBoard, app.level.selectedCell = None, None
                    app.level.moves += 1
            app.level.previousClickTime = clickTime 
            app.level.previousClickLocation = clickLocation
        
        # check for sucessful completion
        if app.level.board == app.level.solutionBoard:
            app.level.success = True
            if app.currentLevel != 8: # don't store score for level 9
                d = shelve.open('Highest Score.txt')
                highestScore = d[str(app.currentLevel+1)]
                moves = app.level.moves + (2-app.level.hintsRemained)
                # check if moves are less, or equal moves but less time, then update the best score
                if (highestScore == None or highestScore[2] > moves or 
                    (highestScore[2] == moves and highestScore[0]*60+highestScore[1] > app.level.minutes*60+app.level.seconds)):
                    d[str(app.currentLevel+1)] = (app.level.minutes, app.level.seconds, moves)
                    d.close()

def game_onStep(app):
    if not app.level.paused and not app.level.success:
        app.level.deciseconds += 1
        if app.level.deciseconds>10:
            app.level.seconds += 1
            app.level.deciseconds = 0
        if app.level.seconds>60:
            app.level.minutes += 1
            app.level.seconds = 0

def game_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    app.level.drawBoard()
    if not app.level.success:
        app.level.drawWaitingZone()
        if not app.level.paused:
            app.level.drawPauseButton()
        else: # draw Paused Page
            drawRect(0, 0, app.width, app.height, fill='black', opacity = 75)
            app.level.drawPlayButton()
            drawRoundedRect(app.width/2,app.height/2,150,75,rgb(55,55,100))
            drawLabel('Paused', app.width/2,app.height/2, fill= 'white', size=25, bold=True)
    app.level.drawExitButton()
    app.level.drawRestartButton()
    app.level.drawHintButton()
    app.level.drawSmartHintButton()
    app.level.drawTimerAndSuccess()
    drawLabel(f'Level {app.currentLevel+1}', 45, 25, fill='white', bold=True, size=15)

def home_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    drawRoundedRect(app.width/2, 75, 225, 75, rgb(55,55,100)) 
    drawLabel('Levels', app.width/2, 75, size=25, fill='white', bold=True)
    i=0
    blues = [rgb(188,211,231),rgb(107,142,183),rgb(79,114,152),rgb(50,82,123),rgb(37,71,109)]
    for row in range(5):
        for col in range(2):
            if i<9:
                i+=1
                if i==9 and app.multiplayerMode: 
                    continue # don't draw level 9 if in multiplayer mode
                color = blues[row]
                drawRoundedRect(app.width/2-75+150*col,200+125*row,75,75,color)
                drawLabel(f'0{i}', app.width/2-75+150*col,200+125*row, size=25, bold=True)
    drawExitButton(app)
    
    if not app.multiplayerMode:
        drawMultiplayerButton(app)
    else:
        drawSingleplayerButton(app)

def home_onMousePress(app,mouseX, mouseY):
    if whichLevelButton(app,mouseX, mouseY) != None:
        app.currentLevel = whichLevelButton(app,mouseX, mouseY)-1
        if app.currentLevel==8: # update the onAppStart for level 9's screen "playerLevel"
            app.board9 = [[False] * 5 for i in range(5)]
            app.lines = {} # {lineNum:('v'or'h',num)}
            app.draggedLine = []
            app.draggedLineDirection = None
            app.active = False
            app.i = 0 # lineNum
            app.currentLine = []
            app.level9PrefilledNum = 0
            setActiveScreen('playerLevel')
        else: 
            if not app.multiplayerMode:
                loadBoardLevel(app)
                board, prefilledNum = app.boardLevels[app.currentLevel]
                app.level = Level(board, prefilledNum,app.currentLevel)
                setActiveScreen('game')
            else: # enter multiplayer screen
                loadBoardLevel(app)
                board, prefilledNum = app.boardLevels[app.currentLevel]
                app.level = twoPlayerLevel(board, prefilledNum, app.currentLevel)
                setActiveScreen('multiPlayerGame')
    
    #check if click on Exit Button
    exitButtonX, exitButtonY = 40, app.height-50
    imageWidth, imageHeight = getImageSize(app.exitButton)
    width = imageWidth//75
    if exitButtonX-width/2 <= mouseX <= exitButtonX+width/2 and exitButtonY-width/2 <= mouseY <= exitButtonY+width/2:
        setActiveScreen('play')

    #check if click on multi/singleplayer Button
    if not app.multiplayerMode:
        buttonX, buttonY = app.width-40, app.height-50
        imageWidth, imageHeight = getImageSize(app.multiPlayerButton)
        width,height = imageWidth//60, imageHeight//60
        if buttonX-width/2 <= mouseX <= buttonX+width/2 and buttonY-height/2 <= mouseY <= buttonY+height/2:
            app.multiplayerMode = True
    else:
        buttonX, buttonY = app.width-40, app.height-50
        imageWidth, imageHeight = getImageSize(app.singlePlayerButton)
        width,height = imageWidth//60, imageHeight//60
        if buttonX-width/2 <= mouseX <= buttonX+width/2 and buttonY-height/2 <= mouseY <= buttonY+height/2:
            app.multiplayerMode = False

def whichLevelButton(app,mouseX, mouseY):
    i = 0
    for row in range(5):
        for col in range(2):
            i += 1
            if i == 9 and app.multiplayerMode: # no level 9 for multiplayer mode
                return None
            cX,cY = app.width/2-75+150*col,200+125*row
            buttonSize = 75
            if (cX-buttonSize/2) <= mouseX <= (cX+buttonSize/2) and (cY-buttonSize/2) <= mouseY <= (cY+buttonSize/2):
                return i
    return None
            
def play_redrawAll(app):
    drawLabel('Blendoku', app.width/2, 100, size=40, bold=True, fill='black')
    drawRoundedRect(app.width/2, app.height/2, 125, 75, rgb(55,55,100))
    drawLabel('Play', app.width/2, app.height/2, size=35, bold=True, fill='white')
    drawRoundedRect(app.width/2, app.height-50, 150, 50, 'gray')
    drawLabel('Instructions', app.width/2, app.height-50, size=20, bold=True, fill='white')
    drawExitButton(app)

def play_onMousePress(app,mouseX,mouseY):
    if (app.width/2-62) <= mouseX <= (app.width/2+62) and (app.height/2-37) <= mouseY <= (app.height/2+37):
        setActiveScreen('home')
    if (app.width/2-75) <= mouseX <= (app.width/2+75) and (app.height-50-25) <= mouseY <= (app.height-50+25):
        setActiveScreen('instruction')

def instruction_redrawAll(app):
    left = 40
    drawRect(0, 0, app.width, app.height, fill='black')
    drawLabel('Your goal: organize squares of color', left, 50, size = 18, fill='white',align='left')
    drawLabel('swatches into a gradient.', left, 75, size = 18, fill='white',align='left')
    y = 120
    spacing = 20
    spacingL = 30
    drawLabel('How to Play:', left,y,fill='white', size=18, bold=True, align='left')
    y += spacingL
    drawLabel('Click to move the colors from the top waiting', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('zone to the bottom board.', left, y, size = 15, fill='white',align='left')
    y += spacingL
    drawLabel('Complete each level with the fewest moves,', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('and once accomplished, aim for the fastest', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('completion time.', left, y, size = 15, fill='white',align='left')
    y += spacingL
    drawLabel('You have two hints for each game. Using hints', left, y, size = 15, fill='white', align='left')
    y += spacing
    drawLabel('will add to the number of moves.', left, y, size = 15, fill='white', align='left')
    y += spacing
    drawLabel('Click the hint button and then click on the square', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('where you want the correct color to be filled.', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('Click the smart hint button to automatically fill', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('the most useful cell currently.', left, y, size = 15, fill='white',align='left')
    y += spacingL
    drawLabel('Double-click on a square to lock it.', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('Double-click again to unlock.', left, y, size = 15, fill='white',align='left')
    y += spacingL
    drawLabel('In two-player mode, each player takes turn', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('placing 2 colors on the board. Each empty cell is', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('associated with points. Correctly filled colors', left, y, size = 15, fill='white',align='left')
    y += spacing
    drawLabel('contribute to the overall score.', left, y, size = 15, fill='white',align='left')

    #draw restart button demo
    imageWidth, imageHeight = getImageSize(app.restartButton)
    drawImage(app.restartButton, 55, 555, align = 'center', width=imageWidth//70, height=imageHeight//70)
    drawLabel('Restart', 85, 555, size = 18, fill='white',align='left',bold=True)
    #draw exit button demo
    imageWidth, imageHeight = getImageSize(app.exitButton)
    drawImage(app.exitButton, 245, 555, align = 'center', width=imageWidth//75, height=imageHeight//75)
    drawLabel('Exit', 275, 555, size = 18, fill='white',align='left',bold=True)
    #draw hint button demo
    imageWidth, imageHeight = getImageSize(app.hintButton)
    drawImage(app.hintButton, 55, 605, align = 'center', width=imageWidth//70, height=imageHeight//70)
    drawLabel('2', 55, 585, fill='white', bold=True)
    drawLabel('Hint', 85, 605, size = 18, fill='white',align='left',bold=True)
    #draw smart hint button demo
    imageWidth, imageHeight = getImageSize(app.smartHintButton)
    drawImage(app.smartHintButton, 245, 605, align = 'center', width=imageWidth//75, height=imageHeight//75)
    drawLabel('2', 245, 625, fill='white', bold=True)
    drawLabel('Smart Hint', 275, 605, size = 18, fill='white',align='left',bold=True)
    #draw pause button demo
    imageWidth, imageHeight = getImageSize(app.pauseButton)
    drawImage(app.pauseButton, 55, 655, align = 'center', width=imageWidth//75, height=imageHeight//75)
    drawLabel('Pause', 85, 655, size = 18, fill='white',align='left',bold=True)
    #draw multiplayer button demo
    imageWidth, imageHeight = getImageSize(app.multiPlayerButton)
    drawImage(app.multiPlayerButton, 245, 655, align = 'center', width=imageWidth//60, height=imageHeight//60)
    drawLabel('2-Player', 275, 655, size = 18, fill='white',align='left',bold=True)
     #draw singleplayer button demo
    imageWidth, imageHeight = getImageSize(app.singlePlayerButton)
    drawImage(app.singlePlayerButton, 245, 705, align = 'center', width=imageWidth//60, height=imageHeight//60)
    drawLabel('1-Player', 275, 705, size = 18, fill='white',align='left',bold=True)

    drawExitButton(app)

def instruction_onMousePress(app,mouseX,mouseY):
    #check if click on Exit Button
    exitButtonX, exitButtonY = 40, app.height-50
    imageWidth, imageHeight = getImageSize(app.exitButton)
    width = imageWidth//75
    if exitButtonX-width/2 <= mouseX <= exitButtonX+width/2 and exitButtonY-width/2 <= mouseY <= exitButtonY+width/2:
        setActiveScreen('play')

def drawExitButton(app):
    imageWidth, imageHeight = getImageSize(app.exitButton)
    drawImage(app.exitButton, 40, app.height-50, align = 'center', width=imageWidth//75, height=imageHeight//75)

def drawMultiplayerButton(app):
    imageWidth, imageHeight = getImageSize(app.multiPlayerButton)
    drawImage(app.multiPlayerButton, app.width-40, app.height-50, align = 'center', width=imageWidth//60, height=imageHeight//60)

def drawSingleplayerButton(app):
    imageWidth, imageHeight = getImageSize(app.singlePlayerButton)
    drawImage(app.singlePlayerButton, app.width-40, app.height-50, align = 'center', width=imageWidth//60, height=imageHeight//60)

# screen for level 9
def playerLevel_onAppStart(app):
    app.board9 = [[False] * 5 for i in range(5)]
    app.rows = 5
    app.cols = 5
    app.boardLeft = 50
    app.boardTop = 250
    app.boardWidth = 300
    app.boardHeight = 300
    app.cellBorderWidth = 2
    
    app.lines = {} # {lineNum:('v'or'h',num)}
    app.draggedLine = []
    app.draggedLineDirection = None
    app.active = False
    app.i = 0 # lineNum
    app.currentLine = []

    app.level9PrefilledNum = 0

def playerLevel_onMousePress(app, mouseX, mouseY):
    #check if click on Exit Button
    exitButtonX, exitButtonY = 40, app.height-50
    imageWidth, imageHeight = getImageSize(app.exitButton)
    width = imageWidth//75
    if exitButtonX-width/2 <= mouseX <= exitButtonX+width/2 and exitButtonY-width/2 <= mouseY <= exitButtonY+width/2:
        setActiveScreen('home')
        
    #check if click on determine prefilled cells
    for i in range(3):
        cx, cy = 145+(i+1)*60, 600
        if cx-25 <= mouseX <= cx+25 and cy-25 <= mouseY <= cy+25:
            app.level9PrefilledNum = i+1

    #check if click on Done Button
    if (app.level9PrefilledNum != 0 
        and (app.width/2-50) <= mouseX <= (app.width/2+50) and (675-25) <= mouseY <= (675+25)
        and app.board9 != [[False] * 5 for i in range(5)]):
        app.board9Empty = copy.deepcopy(app.board9)
        app.level = Level(app.board9, app.level9PrefilledNum, 8)
        setActiveScreen('game')

    startCell = getCell(app,mouseX, mouseY)
    if startCell != None:
        app.active = True
        row,col = startCell
        app.currentLine.append((row,col))
        app.draggedLine.append((row,col))
    
def playerLevel_onMouseDrag(app,mouseX,mouseY):
    if app.active:
        cell = getCell(app,mouseX, mouseY)
        if cell != None and cell not in app.draggedLine:
            row,col = cell
            if legalDirection(app,row,col):
                app.draggedLine.append((row,col))
                app.currentLine.append((row,col))
                if app.draggedLineDirection == None:
                    row1,col1 = app.draggedLine[0]
                    app.draggedLineDirection = (row-row1,col-col1)
            else:
                app.active = False
                app.currentLine = []
                app.draggedLine = []

def playerLevel_onMouseRelease (app,mouseX,mouseY):
    app.active = False
    if len(app.draggedLine) >= 3:
        direction = 'v' if app.draggedLineDirection in [(1,0),(-1,0)] else 'h'
        num = app.draggedLine[-1][0] if direction == 'h' else app.draggedLine[-1][-1]
        coloredCellsNum = countCurrentFilledCellNum(app)
        if legalLine(app,direction,num) and coloredCellsNum+len(app.draggedLine) <= 16:
            for row,col in app.draggedLine:
                app.board9[row][col] = None
            app.lines[app.i] = (direction,num)
            app.i += 1
    app.currentLine = []
    app.draggedLine = []
    app.draggedLineDirection = None

# legal = no change in direction and no diagnoal direction
def legalDirection(app,row,col):
    if len(app.draggedLine) > 1:
        lastInLine = app.draggedLine[-1]
        return (row-lastInLine[0], col-lastInLine[1]) == app.draggedLineDirection
    return True
    
def legalLine(app,direction,num):
    for line in app.lines:
        direction1, num1 = app.lines[line][0], app.lines[line][1]
        if direction1 == direction and abs(num1-num) == 1:
            return False
    return True

def countCurrentFilledCellNum(app):
    count = 0
    for row in range(5):
        for col in range(5):
            if app.board9[row][col] != False:
                count += 1
    return count

def playerLevel_redrawAll(app):
    drawRect(0,0,app.width,app.height,fill='black')
    drawExitButton(app)
    drawBoard(app)
    drawBoardBorder(app)
    for row,col in app.currentLine:
        drawCell(app,row,col,'gray')
    #draw Done button
    drawRoundedRect(app.width/2, 675, 100, 50, rgb(55,55,100))
    drawLabel('Done', app.width/2, 675, size=20, bold=True, fill='white')
    #draw Instructions
    left = 50
    y = 100
    spacing = 25
    drawLabel('Create your own board', app.width/2, 50, size=20, bold=True, fill='white')
    drawLabel('Rules:',left, y, size=18, bold=True, fill='white',align='left')
    y += spacing
    drawLabel('- Draw one line at a time.',left, y, size=16, fill='white',align='left')
    y += spacing
    drawLabel('- Lines of the same direction cannot',left, y, size=16, fill='white',align='left')
    y += spacing-5
    drawLabel('  be adjacent to one another.',left, y, size=16, fill='white',align='left')
    y += spacing
    drawLabel('- Each line has to be 3 cells or longer.',left, y, size=16, fill='white',align='left')
    y += spacing
    drawLabel('- Max filled cells = 16',left, y, size=16, fill='white',align='left')

    #draw user determine prefilled cells
    drawRoundedRect(110, 600, 120, 50, rgb(55,55,100))
    drawLabel('Prefilled:', 110, 600, size=20, bold=True, fill='white')
    blues = rgb(79,114,152),rgb(50,82,123),rgb(37,71,109)
    for i in range(3):
        if i+1 == app.level9PrefilledNum:
            color, textColor = 'white','black'
        else:
            color, textColor = blues[i], 'white'
        drawRoundedRect(145+(i+1)*60, 600, 50, 50, color)
        drawLabel(i+1, 145+(i+1)*60, 600, size=20, bold=True, fill=textColor)

def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board9[row][col]==None:
                drawCell(app, row, col,'white')
            else:
                drawCell(app, row, col, None)

def drawBoardBorder(app):
  # draw the board outline (with double-thickness):
  drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
           fill=None, border='white',
           borderWidth=2*app.cellBorderWidth)

def drawCell(app, row, col,color):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    drawRect(cellLeft, cellTop, cellWidth, cellHeight,
             fill=color, border='white',
             borderWidth=app.cellBorderWidth)

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def getCell(app,x,y):
    dy = y - app.boardTop
    dx = x - app.boardLeft
    row = math.floor(dy/(app.boardWidth / app.rows))
    col = math.floor(dx/(app.boardWidth / app.cols))
    if 0<=row<app.rows and 0<=col<app.cols:
        return (row,col)
    return None

runAppWithScreens(width=400, height=800, initialScreen='play')