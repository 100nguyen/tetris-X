#!/usr/bin/python

"""
ZetCode PyQt6 tutorial

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com

Adapted by Bach Nguyen
"""

import random
import sys
import threading, queue

from PyQt6.QtCore import Qt, QBasicTimer, pyqtSignal, QObject, pyqtSlot, QRect
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (QFrame, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox,
    QWidget, QMainWindow,  QApplication)


class Tetris(QMainWindow):

    main_score = 0
    main_level = 0
    main_lines = 0
    
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        """initiates application UI"""

        # LEFT FRAME                
        hbox = QHBoxLayout()
        
        self.left = QVBoxLayout()
        
        scoreTitle = QLabel('SCORE')       
        self.scoreValue = QLabel('0')
        self.scoreValue.setStyleSheet("color: cyan;"
                                      "background-color: black;") 
        self.scoreValue.setAlignment(Qt.AlignmentFlag.AlignRight)     
        self.left.addWidget(scoreTitle)
        self.left.addWidget(self.scoreValue)
 
        levelTitle = QLabel('LEVEL')       
        self.levelValue = QLabel('0') 
        self.levelValue.setStyleSheet("color: white;"
                                      "background-color: black;")         
        self.levelValue.setAlignment(Qt.AlignmentFlag.AlignRight)                                    
        self.left.addWidget(levelTitle)
        self.left.addWidget(self.levelValue)
 
        linesTitle = QLabel('LINES')       
        self.linesValue = QLabel('0')
        self.linesValue.setStyleSheet("color: yellow;"
                                      "background-color: black;")         
        self.linesValue.setAlignment(Qt.AlignmentFlag.AlignRight)  
        self.left.addWidget(linesTitle)
        self.left.addWidget(self.linesValue)
                      
        self.left.addStretch(1)  
 
         # CENTER FRAME - Board                         
        self.tboard = Board(self)

         # RIGHT FRAME - Queue                 
#        self.right = QFrame()
#        self.right.setFrameShape(QFrame.Shape.StyledPanel)
        self.right = Board_base(self)
        
        hbox.addLayout(self.left)
        hbox.addWidget(self.tboard)
        hbox.addWidget(self.right)
        
        centralWidget = QWidget()
        
        centralWidget.setLayout(hbox)
        self.setCentralWidget(centralWidget)
        
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("color: black;"
                                     "background-color: green;")
                                     
        # Connect the Board's signals to slots                                     
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.tboard.lines_cleared.connect(self.on_lines_cleared)
        self.tboard.nextShape.connect(self.right.on_nextShape)
         
        # start game                
        self.tboard.start()
        
#        self.resize(180, 380)
        self.resize(180*3, 380) #
#        self.resize(270*3, 570)    # x1.5   
        self.center()
        self.setWindowTitle('Tetris')
        self.show()


    def center(self):
        """centers the window on the screen"""

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())


    # A slot for the "lines_cleared" signal, accepting the number of lines cleared in this round
    @pyqtSlot(int)
    def on_lines_cleared(self, n):
        print('Number of lines cleared (%s) in this round.' % (n))

        # Update and display SCORE
        self.main_lines += n
        self.linesValue.setNum(self.main_lines)
        print('\tmain_lines: %s.' % (self.main_lines))

        # Update and display LEVEL        
        self.main_level = self.main_lines // 10
        self.levelValue.setNum(self.main_level)        
        print('\tmain_level: %s' % (self.main_level)) 

        # n |		Points
        #=================================
        # 1                 40
        # 2                100
        # 3                300
        # 4               1200        
        point_table = [40, 100, 300, 1200]
            
        self.main_score += (self.main_level + 1)*point_table[n - 1] 
        self.scoreValue.setNum(self.main_score)      
        print('\tmain_score: %s' % (self.main_score)) 
            
# start of Right Board
class Board_base(QFrame):
    
    BoardWidth = 10
    BoardHeight = 22

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()


    def initBoard(self):
        """initiates board"""

        self.curX = 5
        self.curY = 5

        self.board = [] # origin (0, 0) is the bottom left corner

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet('background-color: black;') 
        self.setFixedSize(180, 380)         
#        self.setFixedSize(270, 570) # 1.5x
        
        self.clearBoard()
        self.update()

    def shapeAt(self, x, y):
        """determines shape at the board position"""

        return self.board[(y * Board.BoardWidth) + x]


    def setShapeAt(self, x, y, shape):
        """sets a shape at the board"""

        self.board[(y * Board.BoardWidth) + x] = shape


    def squareWidth(self):
        """returns the width of one square"""

        return self.contentsRect().width() // Board.BoardWidth


    def squareHeight(self):
        """returns the height of one square"""

        return self.contentsRect().height() // Board.BoardHeight

    def paintEvent(self, event):
        """paints all shapes of the game"""

        painter = QPainter(self)
        rect = self.contentsRect()

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()

#        for i in range(Board.BoardHeight):
#            for j in range(Board.BoardWidth):
#                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

#                if shape != Tetrominoe.NoShape:
#                    self.drawSquare(painter,
#                                    rect.left() + j * self.squareWidth(),
#                                    boardTop + i * self.squareHeight(), shape)

        self.curPiece = Shape()
        
        for k in range(1, 8):
#            print(k)
            self.curPiece.setShape(k)

#            self.curX = Board.BoardWidth // 2 + 1
 
            if (k == 1):
                self.curX = 2
                self.curY = 13
            elif (k == 2):
                self.curX = 7
                self.curY = 13                                                               
            elif (k == 3):
                self.curX = 1
                self.curY = 9
            elif (k == 4):
                self.curX = 7
                self.curY = 9                
            elif (k == 5):
                self.curX = 4
                self.curY = 6
            elif (k == 6):
                self.curX = 2
                self.curY = 2
            else: # (k == 7)
                self.curX = 7
                self.curY = 2                                                         
            
#            print( '\t(self.curX, self.curY) is (%s, %s)' % (self.curX, self.curY))
            
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
#                print( '\t(x, y) is (%s, %s)' % (x, y))
                
                self.drawSquare(painter, 
                                rect.left() + x * self.squareWidth(),
                                boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                                self.curPiece.shape())

        # paint next piece
        self.curPiece.setShape(self.next_shape) 
                               
        self.curX = 4
        self.curY = 20
        
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
#            print( '\t\t(x, y) is (%s, %s)' % (x, y))
                
            self.drawSquare(painter, 
                            rect.left() + x * self.squareWidth(),
                            boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                            self.curPiece.shape())

        rect = QRect(10, 15, 25, 25)
        painter.drawRect(rect)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(self.next_shape))
                                        
    def clearBoard(self):
        """clears shapes from the board"""

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)
            

    def drawSquare(self, painter, x, y, shape):
        """draws a square of a shape"""

#        colorTable = [0x008080, # Teal
#                      0x800000, # Maroon
#                      0x00FFFF, # Aqua
#                      0xFF0000, # Red
#                      0x000080, # Navy
#                      0xC0C0C0, # Silver 
#                      0xFFFF00, # Yellow
#                      0x008000] # Green
        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)


    # A slot for the "lines_cleared" signal, accepting the number of lines cleared in this round
    @pyqtSlot(int)
    def on_nextShape(self, shape):
        self.next_shape = shape
        print('Next Shape: (%s).' % (self.next_shape))
        self.update()

  
# end of Right Board
            
# ORIGINAL            
class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)
    
    # Signal emitted when full lines are cleared, carrying the number of lines cleared
    # in this round
    lines_cleared = pyqtSignal(int) 

    # Signal emitted when full lines are cleared, carrying the number of lines cleared
    # in this round
    nextShape = pyqtSignal(int) 
         
    BoardWidth = 10
    BoardHeight = 22
    Speed = 300 # Each 300 ms a new game cycle will start.
    PieceQueueDepth = 3
    
#    score = 0
#    level = 0

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()


    def initBoard(self):
        """initiates board"""

        # TODO: reset LEFT frame

        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False

        self.numPieces = 0

        self.nextPiece = Shape()
        self.nextPiece.setRandomShape()
        print('***  FIRST piece %s ***' % (self.nextPiece.shape()))
                                          
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = [] # origin (0, 0) is the bottom left corner

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet('background-color: gray;') 
        self.setFixedSize(180, 380)         
#        self.setFixedSize(270, 570) # 1.5x
        
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()


    def shapeAt(self, x, y):
        """determines shape at the board position"""

        return self.board[(y * Board.BoardWidth) + x]


    def setShapeAt(self, x, y, shape):
        """sets a shape at the board"""

        self.board[(y * Board.BoardWidth) + x] = shape


    def squareWidth(self):
        """returns the width of one square"""

        return self.contentsRect().width() // Board.BoardWidth


    def squareHeight(self):
        """returns the height of one square"""

        return self.contentsRect().height() // Board.BoardHeight


    def start(self):
        """starts game"""

        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()

        self.msg2Statusbar.emit('GOOD LUCK!')

        self.newPiece()
        self.timer.start(Board.Speed, self)


    def pause(self):
        """pauses game"""

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("PAUSED")

        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit('Playing...')
 
        self.update()


    def paintEvent(self, event):
        """paints all shapes of the game"""

        painter = QPainter(self)
        rect = self.contentsRect()

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                                    rect.left() + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != Tetrominoe.NoShape:

            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                            boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                            self.curPiece.shape())


    def keyPressEvent(self, event):
        """processes key press events"""

        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == Qt.Key.Key_Left.value:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key.Key_Right.value:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key.Key_Down.value:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key.Key_Up.value:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key.Key_Space.value:
            self.dropDown()

        elif key == Qt.Key.Key_D.value:
            self.oneLineDown()

        else:
            super(Board, self).keyPressEvent(event)


    def timerEvent(self, event):
        """handles timer event"""

        if event.timerId() == self.timer.timerId():

            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()

        else:
            super(Board, self).timerEvent(event)


    def clearBoard(self):
        """clears shapes from the board"""

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)


    def dropDown(self):
        """drops down a shape"""

        newY = self.curY

        while newY > 0:

            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1

        self.pieceDropped()


    def oneLineDown(self):
        """goes one line down with a shape"""

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()


    def pieceDropped(self):
        """after dropping shape, remove full lines and create new shape"""

        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()


    def removeFullLines(self):
#################################
        """removes all full lines from the board"""

        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.BoardHeight):

            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n += 1

            if n == Board.BoardWidth:
                rowsToRemove.append(i)

        rowsToRemove.reverse()

        for m in rowsToRemove:

            for i in range(m, Board.BoardHeight):
                for j in range(Board.BoardWidth):
                    self.setShapeAt(j, i, self.shapeAt(j, i + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines

            # After full lines are cleared, emit the "lines_cleared" signal
            # with the number of cleared full lines in this round
            self.lines_cleared.emit(numFullLines)
            
            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()
#################################

#        numFullLines = 0
#        rowsToRemove = []

#        for i in range(Board.BoardHeight): # bottom up

#            n = 0
#            line = []
#            for j in range(Board.BoardWidth): # left to right
#                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
#                    line.append(self.shapeAt(j, i))
#                    n += 1

#            if n == Board.BoardWidth:
#                print('row ' + str(i) + ' is full ==> ' + str(line))
#                rowsToRemove.append(i)
                
#                if len(rowsToRemove) == 4:
#                    break;

#        print(rowsToRemove)
#        rowsToRemove.reverse()
#        print(rowsToRemove)
      
#        for i in rowsToRemove:
#            for j in range(Board.BoardWidth):
#                print('\tSHAPE at (' + str(i) + ', ' + str(j) + '): ' + str(self.shapeAt(j, i)))
#                self.setShapeAt(j, i, self.shapeAt(j, i + 1))
                    
#        numFullLines = numFullLines + len(rowsToRemove)

#        if numFullLines > 0:
#            print('numFullLines: ' + str(numFullLines))  
#                                        
#            self.numLinesRemoved += numFullLines
            
#            self.level = self.numLinesRemoved // 10
#            print('level: ' + str(self.level)) 

            # number of clear lines | points
            # 1				40
            # 2			       100
            # 3			       300
            # 4			      1200        
#            point_table = [40, 100, 300, 1200]
            
#            self.score += (self.level + 1)*point_table[numFullLines - 1]       
#            print('score: ' + str(self.score)) 

            # After full lines are cleared, emit the "lines_cleared" signal
            # with the number of cleared full lines in this round
#            self.lines_cleared.emit(numFullLines)

#            self.isWaitingAfterLine = True
#            self.curPiece.setShape(Tetrominoe.NoShape)
#            self.update()


    def newPiece(self):
        """creates a new shape"""
        
        self.numPieces += 1
        print('*** New Piece ID: %s ***' % (self.numPieces))

        self.curPiece = self.nextPiece
        print('***  Current piece %s ***' % (self.curPiece.shape()))
        
        self.nextPiece = Shape()
        self.nextPiece.setRandomShape()              
        self.nextShape.emit(self.nextPiece.shape())
        
#        self.curPiece = Shape()
#        self.curPiece.setRandomShape()
                                                              
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
   
        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            
            reply = QMessageBox.critical(self, 'GAME OVER!',
                        "New Game?", QMessageBox.StandardButton.Yes |
                        QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.initBoard()
                self.start()
                       
            self.msg2Statusbar.emit("Game over!")


    def tryMove(self, newPiece, newX, newY):
        """tries to move a shape"""

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True


    def drawSquare(self, painter, x, y, shape):
        """draws a square of a shape"""

#        colorTable = [0x008080, # Teal
#                      0x800000, # Maroon
#                      0x00FFFF, # Aqua
#                      0xFF0000, # Red
#                      0x000080, # Navy
#                      0xC0C0C0, # Silver 
#                      0xFFFF00, # Yellow
#                      0x008000] # Green
        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)


class Tetrominoe:

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape:

    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):

        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)


    def shape(self):
        """returns shape"""

        return self.pieceShape


    def setShape(self, shape):
        """sets a shape"""

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape


    def setRandomShape(self):
        """chooses a random shape"""

        self.setShape(random.randint(1, 7))


    def x(self, index):
        """returns x coordinate"""

        return self.coords[index][0]


    def y(self, index):
        """returns y coordinate"""

        return self.coords[index][1]


    def setX(self, index, x):
        """sets x coordinate"""

        self.coords[index][0] = x


    def setY(self, index, y):
        """sets y coordinate"""

        self.coords[index][1] = y
        

    def minX(self):
        """returns min x value"""

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m


    def maxX(self):
        """returns max x value"""

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m


    def minY(self):
        """returns min y value"""

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m


    def maxY(self):
        """returns max y value"""

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m


    def rotateLeft(self):
        """rotates shape to the left"""

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result


    def rotateRight(self):
        """rotates shape to the right"""

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result


def main():

    app = QApplication([])
    app.setStyleSheet('.QLabel { font-size: 24pt;}')    
    tetris = Tetris()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

