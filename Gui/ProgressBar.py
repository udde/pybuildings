import sys
from PyQt4 import QtGui, QtCore

class ProgressBarWidget(QtGui.QWidget):
    
    def __init__(self):
        super(ProgressBarWidget, self).__init__()
        
        #self.initUI()
        
    def initUI(self):      

        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        #self.btn = QtGui.QPushButton('Start', self)
        #self.btn.move(40, 80)
        #self.btn.clicked.connect(self.doAction)

        self.timer = QtCore.QBasicTimer()
        self.step = 0
        
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QtGui.QProgressBar')
        self.show()
        #self.doAction()
        
    def timerEvent(self, e):
      
        if self.step >= 100:
        
            self.timer.stop()
            #self.btn.setText('Finished')
            self.close()
            return
            
        self.step = self.step + 3
        self.pbar.setValue(self.step)

    def doAction(self):
      
        if self.timer.isActive():
            self.timer.stop()
            #self.btn.setText('Start')
            
        else:
            self.timer.start(1000, self)
            #self.btn.setText('Stop')
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = ProgressBarWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()   