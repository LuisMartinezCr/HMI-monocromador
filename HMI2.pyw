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
#        self.ui.goscan.clicked.connect(self.go_scan)
#        self.ui.abortscan.clicked.connect(self.abort_scan)
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
        self.ui.units.activated.connect(self.units_)
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

    def units_(self):#deveriamos de  preguntar el estado del shutter o unidades aunque creo q esta de mas
        try:
            state_units = self.ui.units.currentText()
            if state_units == "nm":
                value_units = "UNITS NM" + chr(10)
                self.ser.write(value_units.encode('ascii'))
            elif state_units == "um":
                value_units = "UNITS UM" + chr(10)
                self.ser.write(value_units.encode('ascii'))
            elif state_units == "cm-1":
                value_units = "UNITS WN" + chr(10)
                self.ser.write(value_units.encode('ascii'))
            print(state_units)
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
            
        except:
            self.show_popup()
    def send_(self, ser):
        try:
            comando = self.ui.command.text() + chr(10)#envia lo que escribo en el edit line
            self.ser.write(comando.encode('ascii'))
            print("FUNCION SEND")#DEBUG
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
            
    def show_popup(self): # ver la forma de hacerlo mejor
        msg = QMessageBox()
        msg.setWindowTitle("Error  ")# titulo del mnsj
        elerror = str(sys.exc_info()[0])
        systemerror = elerror.strip(" '' '<>' 'class'")
        msg.setText("Error: " + systemerror)# contexto del messageBox
        msg.setIcon(QMessageBox.Warning)#ponerle un icono
        x = msg.exec_()
    
    def pregunta_error(self):
        pregunta_error = 'ERROR?'+chr(10)#ln
        self.ser.write(pregunta_error.encode('ascii'))
        e = str(self.lectura())
        a = e.split()
        i = a[-1]
        if i == '1' or '2' or '3':
            print("command not understood")
        else:
            pass
        
app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())