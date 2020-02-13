from PyQt5 import QtWidgets, QtGui, QtCore#definir las librerias respetar mayusculas
from interfaz_ui import Ui_MainWindow  # importing our generated file
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
import sys, serial, serial.tools.list_ports, time

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #-------------BOTONES-------------
        self.ui.abortscan.clicked.connect(self.abort_scan)
#        self.ui.goscan.clicked.connect(self.go_scan)
        #------Combobox-------------------
        self.ui.units.addItem("nm")
        self.ui.units.addItem("um")
        self.ui.units.addItem("cm-1")
        
        self.ui.shutter.addItem("Closed")
        self.ui.shutter.addItem("Open")
        
        self.ui.presentwave.setReadOnly(True) # desavilita los editline
        self.ui.response.setReadOnly(True)
        self.ui.setwave.setMaxLength(4)
        self.ui.setwave.setValidator(QtGui.QDoubleValidator())#solo entra numeros
        #-----funcion lineEdit "Send" con Enter
        self.ui.send.clicked.connect(self.send_)
        self.ui.send.setAutoDefault(True)
        self.ui.command.returnPressed.connect(self.ui.send.click)#funcion para que lineEdit accione algo al presionar enter
        self.ui.setwave.returnPressed.connect(self.setwave_)#funcion para que lineEdit accione algo al presionar enter

        self.ui.conectar.clicked.connect(self.conectar_)
        self.ui.refresh.clicked.connect(self.refresh_)
        
        self.ui.shutter.activated.connect(self.shutter_)
        
    def conectar_(self):
        namep = self.ui.port.currentText()
        try:
            self.ser = serial.Serial(namep, 9600, timeout=1)
            if (self.ser.isOpen() == True):
                self.ui.state.setText("Connected")
        except:
            self.ui.state.setText("Disconnected")
            
    def refresh_(self):
        self.ui.port.clear()       
        for comport in serial.tools.list_ports.comports():
            self.ui.port.addItem(comport.device)
        namep = self.ui.port.currentText()
        
        
    def lectura(self):
        res = bytearray()#se crea un lista para almacenar bytes "res" de tamaño 0
        while True:
            a = self.ser.read(1)#cada caracter es leido y almacenado a "a"
            print(a)
            if a:
                res += a        #se acumulan en "res"
                if res[-1] == ord('\r'):#ord convierte de char a entero en este caso "\r" = 13 si el ultimo byte de la lista es 13 imprime "res"
                    print(res)#DEBUG
                    break
            else:
                break
        return res.decode('ascii').strip("\r \ \n")
    
    def shutter_(self):
        try:
            estadoshutter = self.ui.shutter.currentText()
            if estadoshutter == "Closed":
                estado = "SHUTTER C" + chr(10)
                self.ser.write(estado.encode('ascii'))
            else:
                estadoshutter == "Open"
                estado = "SHUTTER O" + chr(10)
                self.ser.write(estado.encode('ascii'))
            print(estadoshutter)
        except:
            self.show_popup()
    
    def setwave_(self):
        try:
            comando = 'GOWAVE '+ self.ui.setwave.text() +chr(10)# NECESITA EL ESPACIO EN EL COMANDO
            self.ser.write(comando.encode('ascii'))
            
            coma = 'WAVE?'+chr(10)#ln
            self.ser.write(coma.encode('ascii'))
            
            time.sleep(1) # NOS QUEDAMOS AQUI HAY QUE VER COMO IMPRIMIR MAS DE UNA VEZ EN PRESNETWAVE      
            n_n = self.lectura()
            separador = n_n.split()
            self.ui.presentwave.setText(str(separador[-1]))
            self.shutter_()
            self.pregunta_error()
        except:
            self.show_popup()
    def send_(self, ser):
        try:
            comando = self.ui.command.text() + chr(10)#envia lo que escribo en el edit line
            self.ser.write(comando.encode('ascii'))
            g_g = self.lectura()
            separador = g_g.split()
            self.ui.response.setText(str(separador[-1]))
            self.pregunta_error()
        except AttributeError:
            self.show_popup()
            print("El error es: ",sys.exc_info()[0])
        
        except:
            pass
         #   show_error()
    def abort_scan(self):
        print("abort")
        pregunta_error = 'ABORT'+chr(10)#ln
        self.ser.write(pregunta_error.encode('ascii'))
        print("abortado")
            
    def show_popup(self): # ver la forma de hacerlo mejor
        msg = QMessageBox()
        msg.setWindowTitle("Error  ")# titulo del mnsj
        elerror = str(sys.exc_info()[0])
        systemerror = elerror.strip(" '' '<>' 'class'")
        msg.setText("Error: " + systemerror)# contexto del messageBox
        msg.setIcon(QMessageBox.Warning)#ponerle un icono
        x = msg.exec_()
    
    def show_error(self, condition): # ver la forma de hacerlo mejor
        
        msg = QMessageBox()
        msg.setWindowTitle("Error  ")
        msg.setText(condition)# contexto del messageBox
        msg.setIcon(QMessageBox.Warning)#ponerle un icono
        x = msg.exec_()
        
    def pregunta_error(self):
        pregunta_error = 'ERROR?'+chr(10)#ln
        self.ser.write(pregunta_error.encode('ascii'))
        e = str(self.lectura())
        a = e.split()
        i = a[-1]
        if i == '1':
            variable_error = 'command not understood'
            self.show_error(variable_error)
            print("command not understood")
        elif i == '2':
            variable_error = 'bad parameter used in command'
            self.show_error(variable_error)
            print("bad parameter used in command")
        elif i == '3':
            variable_error = 'destination position for wavelenght motion not allowed'
            self.show_error(variable_error)
            print("destination position for wavelenght motion not allowed")
        elif i == '6':
            variable_error = 'Accesory not present (usually filter wheel)'
            self.show_error(variable_error)
            print("Accesory not present (usually filter wheel)")
        elif i == '7':
            variable_error = 'Accesory already in specified position'
            self.show_error(variable_error)
            print("Accesory already in specified position")
        elif i == '8':
            variable_error = 'Could not home wavelenght drive'
            self.show_error(variable_error)
            print("Could not home wavelenght drive")
        elif i == '9':
            variable_error = 'Label too long'
            self.show_error(variable_error)
            print("Label too long")
        elif i == '0':
            variable_error = 'System error(miscellaneous)'
            self.show_error(variable_error)
            print("System error(miscellaneous)")
        else:
            pass
        
app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())