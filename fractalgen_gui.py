# File containing the code for a GUI using PyQT for running a 
# fractal generator and viewer. 

import sys, os
import datetime
import numpy as np 
from numba import jit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex
import configparser
from PyQt5.QtGui import (QPixmap, QIntValidator, 
                        QIcon, QDoubleValidator,
                        QPainter, QColor, QPen, QBrush)
from PyQt5.QtWidgets import (QWidget, QApplication,
                             QGridLayout, QLabel,
                             QPushButton,QAction,
                             QLineEdit, QMessageBox,
                             QFileDialog, QTextEdit,
                             QFileSystemModel, QTreeView,
                             QHBoxLayout, QVBoxLayout,
                             QComboBox, QDialog ,
                             QSizePolicy)
import fractalGenerator


class FractalGenWindow(QWidget):
    """The main window of the program."""

    #### Initialization #################################
    def __init__(self):
        super().__init__()
        self.initUI()
        self.readConfigFile()

    def initUI(self):
        """sets up the user interface, connects all the signals and shows the window. """

        self.init_components()
        self.connect_signals()

        self.setGeometry(100, 100, 1300, 800)
        self.setWindowTitle('Fractal Generator')
        self.setWindowIcon(QIcon('mandelIcon.png'))
        
        self.setImage("current.png")
        self.fractalSet = None 

        initial_view = self.makeConfig() 
        self.history = [ initial_view ]
        self.history_index = 0 
        
        self.show()

    def readConfigFile(self):
        """Reads the last settings of the program from the config file, if it exists, otherwise sets the
        standard mandelbrot settings.""" 
        config = configparser.ConfigParser()
        self.config = config 
        self.makeConfig()

        if os.path.exists('fractalGen.ini'):
            config.read('fractalGen.ini')
            viewinfo = dict(config.items('View'))
            self.viewConfig.__dict__ = viewinfo
            self.loadConfig(self.viewConfig)
        else:
            self.saveConfig()                 
            
        
    def init_components(self):
        """initializes all components and sets up the layout"""
        internalWidget = QWidget()

        ############ define components ####################
        self.x0Input = QLineEdit("-2.0")
        
        self.x1Input = QLineEdit("1.0")
        self.y0Input = QLineEdit("1.25")
        self.y1Input = QLineEdit("-1.25")
        self.widthInput = QLineEdit("1000")
        self.heightInput = QLineEdit("800") 
        self.filenameInput = QLineEdit() 
        
        self.functionInput = QLineEdit("z**2 + c")
        self.iterlimInput = QLineEdit("30")

        self.onlyInt = QIntValidator()
        self.onlyDouble = QDoubleValidator()

        self.widthInput.setValidator(self.onlyInt)
        self.heightInput.setValidator(self.onlyInt)
        self.iterlimInput.setValidator(self.onlyInt)


        x0Label = QLabel('x0')
        x1Label = QLabel('x1')
        y0Label = QLabel('y0')
        y1Label = QLabel('y1')
        widthLabel = QLabel('Width')
        heightLabel = QLabel('Height')
        functionLabel = QLabel("Function")
        functionHelpLabel = QLabel("Format: python syntax, polynomial in z,c. I**2 = -1. ")
        iterlimLabel = QLabel("Iteration limit")

        self.posLabel = QLabel("Mouse position: (0,0) ")
        # self.dirLabel = QLabel('folder')

        # self.imgView = QLabel()
        self.imgView = FractalViewer(self)

        self.outputText = QTextEdit('')
        self.outputText.setReadOnly(True)

        self.colorschemeCb = QComboBox()
        self.colorschemeCb.addItems([ "Inferno", "Plasma", 
                                 "Viridis", "Magma",
                                 "Spectral", "Seismic",
                                 "HSV", "Prism","Rainbow",
                                 "Flag", "Cividis", 
                                 "Greys", "Greys inverted",
                                 "Blues", "Reds", "Copper", 
                                 "Winter", "Cool"])

        
        colorSchemeLabel = QLabel('Color scheme')

        self.interpCb = QComboBox()
        self.interpCb.addItems([ "Autolog", "Linear",
                             "Gamma 2", "Gamma 3","Gamma 4",
                                "Log 2","Log 3","Log 4",
                                 "Sin" ])

        
        interpLabel = QLabel('Color interpolation')
        
        
        self.runButton = QPushButton('Generate image')
        self.saveButton = QPushButton('save image')
        self.backButton = QPushButton('Back')
        self.resetButton = QPushButton("Reset View")
        # self.fileModel = QFileSystemModel()
        # self.tree = QTreeView()
        # self.tree.setModel(self.fileModel)

        self.outputText = QTextEdit('')
        self.outputText.setReadOnly(True)


        ############# Setup the grid layout###############################
        grid = QGridLayout()
        # grid.addWidget(menu_bar, 1, 0, 1, 4)
        grid.setVerticalSpacing(15)
        grid.setHorizontalSpacing(8)
        grid.addWidget(x0Label, 1,0)
        grid.addWidget(self.x0Input,1,1)
        grid.addWidget(y0Label,1,2)
        grid.addWidget(self.y0Input, 1,3 )

        grid.addWidget(x1Label, 2,0)
        grid.addWidget(self.x1Input,2,1)
        grid.addWidget(y1Label,2,2)
        grid.addWidget(self.y1Input, 2,3 )

        grid.addWidget(widthLabel,3,0)
        grid.addWidget(self.widthInput,3,1)
        grid.addWidget(heightLabel,3,2)
        grid.addWidget(self.heightInput,3,3)

        grid.addWidget(functionLabel,4,0)
        grid.addWidget(self.functionInput,4,1,1,3)

        grid.addWidget(functionHelpLabel,5,0,1,4)

        grid.addWidget(iterlimLabel, 6,0,1,2)
        grid.addWidget(self.iterlimInput,6,2,1,2)

        grid.addWidget(colorSchemeLabel, 7,0, 1,2)
        grid.addWidget(self.colorschemeCb,7,2 ,1,2 )

        grid.addWidget(interpLabel, 8,0,1,2)
        grid.addWidget(self.interpCb,8,2,1,2)

        grid.addWidget(self.runButton,9,0,1,4)
        grid.addWidget(self.backButton, 10,0)
        grid.addWidget(self.saveButton,10,1,1,2)
        grid.addWidget(self.resetButton, 10,3)
        # grid.addWidget(self.dirLabel,8,0,8,3)
        grid.addWidget(self.outputText,11,0,8,4)
        grid.addWidget(self.posLabel,20,0,1,4)
        # grid.addWidget(self.stopButton,5,0)
        # grid.addWidget(self.runButton,5,1)
        


        # grid.addWidget(self.tree,1,3, 11,3)

        #the image viewer, setting how it behaves under resizing.
        # self.imgView.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        # self.imgView.setMaximumHeight(800)
        self.imgView.setFixedHeight(800)
        self.imgView.setFixedWidth(1000)

        internalWidget.setLayout(grid)
        # internalWidget.setMinimumWidth(200)
        # internalWidget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding))
        internalWidget.setFixedWidth(400)
        internalWidget.setFixedHeight(800)
        
        # vbox = QVBoxLayout() 
        # vbox.addWidget(internalWidget)
        # vbox.addWidget(self.posLabel)
        internalWidget.setLayout(grid)


        hbox = QHBoxLayout()
        # hbox.setMenuBar(menu_bar)
        hbox.addWidget(internalWidget)
        hbox.addWidget(self.imgView)

        self.setLayout(hbox)

    
    def connect_signals(self):
        """connects all the signals to the right functions"""
        self.saveButton.clicked.connect(self.showSaveDialog)
        self.runButton.clicked.connect(self.runGenerationThreaded)

        self.backButton.clicked.connect(self.goBack)
        self.resetButton.clicked.connect(self.resetView)

        self.setMouseTracking(True) 
        self.imgView.setMouseTracking(True)

    ############################################################
    ########### Actions ########################################   
       
    def goBack(self):
        """Steps back once in the view-settings history. Does not run the fractal generation. """ 
        if self.history_index != 0 and len(self.history)>1:
            self.history_index -= 1 
            self.loadConfig(self.history[self.history_index])
        return 

    def resetView(self):
        """Resets the view settings to the standard Mandelbrot settings, but does not reset the function.
        Does not run the fractal generation. 
        """ 
        x0 = -2.
        x1 = 1.0
        y0 = 1.25
        y1 = -1.25

        iter_limit = 40
        width = 1000
        height = 800
        function = self.functionInput.text() 

        colorscheme = "Inferno"
        colorinterp = "Autolog" 

        self.viewConfig = ViewConfig(x0,x1,y0,y1,width,height,function,
                        iter_limit, colorscheme, colorinterp)
        self.loadConfig(self.viewConfig)
     
    def runGenerationThreaded(self):
        """What happens when the user clicks the 'generate' button.
        Creates a thread to run the fractal generation, and runs it. """ 
        view = self.makeConfig() 
        if self.validateFunction():
            self.saveConfig() 
            self.history.append(view)
            self.history_index = len(self.history)-1 

            ViewChanged = self.checkViewChange()


            filename = "current"

            if ViewChanged:
                self.get_thread = FractalGenThread(view,filename,self)
            else:
                self.get_thread = FractalGenThread(view, filename,self,set=self.fractalSet)
            self.get_thread.changeText.connect(self.update_output_text)
            self.get_thread.finished.connect(self.image_finished)
            # self.get_thread.finished.connect(self.setImage)

            # self.update_output_text("Starting... ")
            
            self.get_thread.start() 
        else: 
            msgBox = QMessageBox()
            
            msgBox.setWindowIcon(QIcon("mandelIcon.png"))
            msgBox.setText('Please input a valid function.\n \n \
                It should only involve numbers, I, z and c, and be written in Python syntax. \n \
                All multiplication should be written out (i.e. 2*z, not 2z), exponents are written as z**2 etc..\n \
                No use of elementary functions like sin,exp etc. is allowed. ')
            msgBox.setWindowTitle("Invalid function syntax")
            msgBox.exec_()
            pass 

    def showSaveDialog(self):
        """Shows the dialog to choose where to save the current image, and saves it as a png-file.""" 
        dlg = QFileDialog()
        filepath = dlg.getSaveFileName(None, "Save current image as", "", "png (*.png)")
        self.imgView.pixmap.save(filepath[0])
        return filepath
   

    #############################################################
    ######## helper functions####################################

    def setImage(self, filepath):
        """Sets the image of the imageViewer, if the specified file exists. Otherwise leaves it blank.""" 
        self.imgView.filepath = filepath 
        if os.path.exists(filepath):
            self.imgView.pixmap=QPixmap(filepath)
        
    @pyqtSlot(str)
    def update_output_text(self, message:str):
        """updates the output text area. """
        self.outputText.setText(self.outputText.toPlainText() + message)
         

    @pyqtSlot()
    def image_finished(self):
        #reset rectangle coordinates, so that it's no longer drawn. 
        self.imgView.rect_x0p=-1
        self.imgView.rect_y0p=-1
        #reload the image:
        self.imgView.pixmap=QPixmap(self.imgView.filepath)
        self.imgView.update()

    def checkViewChange(self):
        """Checks if the user changed the view settings so that we have to 
        generate a new fractal set, or if only the color settings were changed, 
        in which case we can reuse the last generated set. """ 
        if len(self.history)<=1:
            return True
        else:
            current = self.history[-1]
            previous = self.history[-2]

            if (current.x0 == previous.x0) and (current.x1==previous.x1) \
                and (current.y0 == previous.y0) and (current.y1 == previous.y1) \
                and (current.width == previous.width) and (current.height==previous.height)\
                and (current.iter_limit == previous.iter_limit) and (current.function==previous.function) : 
                return False 
            else: 
                return True 

    def loadConfig(self,cfg ):
        """Sets all the settings as specified from the config-class"""
        self.x0Input.setText("{0:.7f}".format(float(cfg.x0)))
        self.x1Input.setText("{0:.7f}".format(float(cfg.x1)))
        self.y0Input.setText("{0:.7f}".format(float(cfg.y0)))
        self.y1Input.setText("{0:.7f}".format(float(cfg.y1)))
        self.widthInput.setText(str(cfg.width))
        self.heightInput.setText(str(cfg.height))
        # self.heightInput.setText(str(cfg.height))
        self.functionInput.setText(cfg.function)
        self.iterlimInput.setText(str(cfg.iter_limit))

        self.colorschemeCb.setCurrentText(cfg.colorscheme)
        self.interpCb.setCurrentText(cfg.colorinterp)

        cfg.x0 = float(cfg.x0)
        cfg.x1 = float(cfg.x1)
        cfg.y0 = float(cfg.y0)
        cfg.y1 = float(cfg.y1)
        cfg.height = int(cfg.height)
        cfg.width = int(cfg.width)
        cfg.iter_limit = int(cfg.iter_limit)
        

        self.imgView.x0 = cfg.x0
        self.imgView.x1 = cfg.x1
        self.imgView.y0 = cfg.y0
        self.imgView.y1 = cfg.y1

    def makeConfig(self):
        """Reads current settings and creates a corresponding config-class. 
        Also sets the created config as the current config. """
        x0 = float(self.x0Input.text() )
        x1 = float(self.x1Input.text() )
        y0 = float(self.y0Input.text() )
        y1 = float(self.y1Input.text() )

        iter_limit = int(self.iterlimInput.text() )
        width = int(self.widthInput.text() )
        height = int(self.heightInput.text() )
        function = self.functionInput.text() 

        colorscheme = self.colorschemeCb.currentText() 
        colorinterp = self.interpCb.currentText() 

        self.imgView.x0 = x0
        self.imgView.x1 = x1
        self.imgView.y0 = y0
        self.imgView.y1 = y1

        self.viewConfig = ViewConfig(x0,x1,y0,y1,width,height,function,
                        iter_limit, colorscheme, colorinterp)
        return self.viewConfig

    def saveConfig(self):
        """Saves the current config to the config (.ini) file, so that it can be loaded the next time the program is run.""" 
        view = self.viewConfig 
        self.config['View'] = {
            'x0' : view.x0,
            'x1' : view.x1,
            'y0' : view.y0,
            'y1' : view.y1,
            'width' : view.width,
            'height' : view.height,
            'iter_limit':view.iter_limit,
            'colorscheme':view.colorscheme,
            'colorinterp':view.colorinterp,
            'function':view.function       
        }
        with open('fractalGen.ini','w') as configfile:
            self.config.write(configfile)

    def validateFunction(self):
        try:
            function = self.functionInput.text() 
            lambdastr=f'lambda z,c:'+function.replace("I",'complex(0,1)')
            lambdafunc = eval(lambdastr)
            func = jit(nopython=True)(lambdafunc)
            r1 = func(complex(1,1), complex(0.2,-0.4))
            r2 = func(complex(-0.1,-2), complex(-3,4))
            return True
        except:
            return False 
        


class FractalGenThread(QThread):
    """Defines the thread that generates the fractal"""

    changeText = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, view, filename:str, parent, set=None):

        self.parent = parent 
        if type(set) != type(None):
            self.set=set
            self.useStoredSet=True
        else:
            self.useStoredSet=False 

        QThread.__init__(self)
        self.view = view 

        filepath = os.path.join(os.getcwd(), filename)

        self.filepath = filepath #os.path.join(base_folder,filename)

        # self.changeText = pyqtSignal(str)

    def __del__(self):
        self.wait()

    def run(self):
        """Runs the fractal generation and at the end, displays the new image in the image-viewer (through the finished signal)"""
        self.changeText.emit('Generating ... ')
        view = self.view 
        if not self.useStoredSet:            
            
            set, time = fractalGenerator.get_fractal_set(
                view.function, view.x0, view.x1,
                view.y1, view.y0, 
                view.width, view.height, view.iter_limit
            )
            self.parent.fractalSet = set 
        else:
            set = self.set 
            time = 0.001 

        
        set = fractalGenerator.rescale(set,view.iter_limit, view.colorinterp)
        fractalGenerator.save_image(set, self.filepath, view.colorscheme)

        self.finished.emit()
        self.changeText.emit( "took {0:.4f}".format(time) + ' seconds \n')


class FractalViewer(QLabel):
    """The widget that displays the fractal.
    Implements methods for selecting a new viewport, 
    and rendering the selection rectangle showing 
    which part we are zooming in about"""
    def __init__(self, parent_window):
        super().__init__()

        self.mousePressed = False 
        self.parent = parent_window
        self.filepath="" 
        # self.pixmap = QPixmap(self.parent.filepath)

        self.x0 = -2
        self.y0 = 1.25
        self.x1 = 1
        self.y1 = -1.25

        
        self.rect_x0p = -100
        self.rect_y0p = -100
        # self.rect_x1p = -100
        # self.rect_y1p = -100
        
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        w = self.pixmap.scaledToHeight(800).width()
        h = self.geometry().height() 
        x = event.x()
        y = event.y()
        if self.mousePressed :
            self.rect_dx = x - self.rect_x0p
            self.rect_dy = y - self.rect_y0p
            self.update() 

        x = self.x0 + x*(self.x1-self.x0)/w
        y = self.y0 - y*(self.y0-self.y1)/h

        self.parent.posLabel.setText("Mouse position : ( {0:.8f}".format(x) +", {0:.8f}".format(y) + ")" ) 

    def mousePressEvent(self,event):
        self.mousePressed = True 
        w = self.pixmap.scaledToHeight(800).width()
        h = self.geometry().height() 
        x = event.x()
        y = event.y()
        self.rect_x0p = x
        self.rect_y0p = y 

        x = self.x0 + x*(self.x1-self.x0)/w
        y = self.y0 - y*(self.y0-self.y1)/h

        self.rect_x0 = x
        self.rect_y0 = y 

        self.parent.x0Input.setText("{0:.7f}".format(x) )
        self.parent.y0Input.setText("{0:.7f}".format(y) )


    def mouseReleaseEvent(self,event):
        self.mousePressed=False 
        w = self.pixmap.scaledToHeight(800).width()
        h = self.geometry().height() 
        x = event.x()
        y = event.y()

        x = self.x0 + x*(self.x1-self.x0)/w
        y = self.y0 - y*(self.y0-self.y1)/h

        ##make sure that the upper-left point goes to (x0,y0)
        x0t = min(x,self.rect_x0)
        y0t = max(y,self.rect_y0)
        x1t = max(x, self.rect_x0)
        y1t = min(y, self.rect_y0)

        self.rect_x0 = x0t
        self.rect_y0 = y0t 
        self.rect_x1 = x1t
        self.rect_y1 = y1t 

        # self.rect_dx = self.rect_x1 - self.rect_x0 
        # self.rect_dy = self.rect_y0 - self.rect_y1 


        #update the numbers in the boxes 
        self.parent.x0Input.setText("{0:.7f}".format(self.rect_x0) )
        self.parent.y0Input.setText("{0:.7f}".format(self.rect_y0) )
        self.parent.x1Input.setText("{0:.7f}".format(self.rect_x1) )
        self.parent.y1Input.setText("{0:.7f}".format(self.rect_y1) )
        self.update() 

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        if self.filepath != "" : 
            qp.drawPixmap(0,0,self.pixmap.scaledToHeight(800))
        
        self.drawRectangle(qp)
        qp.end()

        
    def drawRectangle(self, qp):
        """draws the 'zooming' rectangle onto the fractal"""
        col = QColor(0, 0, 0)
        # col.setNamedColor('#d4d4d4')
        qp.setPen(col)
        if self.rect_x0p > 0 and self.rect_y0p > 0 :
            qp.drawRect(self.rect_x0p,self.rect_y0p,self.rect_dx,self.rect_dy)
        # qp.setBrush(QColor(200, 0, 0))
        # qp.drawRect(10, 15, 90, 60)


    
class ViewConfig:
    """Helperclass, stores all the info about the current view. """ 
    def __init__(self, x0,x1,y0,y1,width,height,function,iter_limit, colorscheme, colorinterp):
        self.x0=x0
        self.x1=x1
        self.y0=y0
        self.y1=y1
        self.width=width
        self.height = height
        self.function = function
        self.iter_limit = iter_limit
        self.colorscheme = colorscheme
        self.colorinterp = colorinterp 
        return 
    


######### Runs the thing: ############
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FractalGenWindow()
    sys.exit(app.exec_())