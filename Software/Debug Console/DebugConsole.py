import tkinter as tk
import tkinter.ttk as ttk
import serial.tools.list_ports
import time
import socket
import select
import math
import threading
from simple_pid import PID
import configparser

filename = "config.ini"











global magDataX
global magDataY
global magDataZ

global accDataX
global accDataY
global accDataZ

global rotDataX
global rotDataY
global rotDataZ

global magXbias, magYbias, magZbias, rotXbias, rotYbias, rotZbias, accXbias, accYbias, accZbias, magXscale, magYscale, magZscale

magDataX = 0 
magDataY = 0 
magDataZ = 0 
accDataX = 0 
accDataY = 0 
accDataZ = 0 
rotDataX = 0 
rotDataY = 0 
rotDataZ = 0 







       


#### connect to wifi 



### take check data from robot from sensor info



class FileCommands:
    def writeIMUConfig():
        global magXbias, magYbias, magZbias, rotXbias, rotYbias, rotZbias, accXbias, accYbias, accZbias, magXscale, magYscale, magZscale

        filename = "config.ini"

        # Writing Data
        config = configparser.ConfigParser()
        config.read(filename)

        try:
            config.add_section("IMU_CONFIG")
        except configparser.DuplicateSectionError:
            pass

        config.set("IMU_CONFIG","magXbias" ,str(magXbias ) )
        config.set("IMU_CONFIG","magYbias" ,str(magYbias ) )
        config.set("IMU_CONFIG","magZbias" ,str(magZbias ) )
        config.set("IMU_CONFIG","rotXbias" ,str(rotXbias ) )
        config.set("IMU_CONFIG","rotYbias" ,str(rotYbias ) )
        config.set("IMU_CONFIG","rotZbias" ,str(rotZbias ) )
        config.set("IMU_CONFIG","accXbias" ,str(accXbias ) )
        config.set("IMU_CONFIG","accYbias" ,str(accYbias ) )
        config.set("IMU_CONFIG","accZbias" ,str(accZbias ) )
        config.set("IMU_CONFIG","magXscale",str(magXscale))
        config.set("IMU_CONFIG","magYscale",str(magYscale))
        config.set("IMU_CONFIG","magZscale",str(magZscale))

        with open(filename, "w") as config_file:
            config.write(config_file)
    
    

    def readIMUConfig():
        global magXbias, magYbias, magZbias, rotXbias, rotYbias, rotZbias, accXbias, accYbias, accZbias, magXscale, magYscale, magZscale

        filename = "config.ini"
        # Reading Data
        config = configparser.ConfigParser()
        config.read(filename)
        magXbias  = float(config.get("IMU_CONFIG","magXbias" ))
        magYbias  = float(config.get("IMU_CONFIG","magYbias" ))
        magZbias  = float(config.get("IMU_CONFIG","magZbias" ))
        rotXbias  = float(config.get("IMU_CONFIG","rotXbias" ))
        rotYbias  = float(config.get("IMU_CONFIG","rotYbias" ))
        rotZbias  = float(config.get("IMU_CONFIG","rotZbias" ))
        accXbias  = float(config.get("IMU_CONFIG","accXbias" ))
        accYbias  = float(config.get("IMU_CONFIG","accYbias" ))
        accZbias  = float(config.get("IMU_CONFIG","accZbias" ))
        magXscale = float(config.get("IMU_CONFIG","magXscale"))
        magYscale = float(config.get("IMU_CONFIG","magYscale"))
        magZscale = float(config.get("IMU_CONFIG","magZscale"))

    def writePIDConfig():
        filename = "config.ini"

        # Writing Data
        config = configparser.ConfigParser()
        config.read(filename)

        try:
            config.add_section("PID_CONFIG")
        except configparser.DuplicateSectionError:
            pass

        config.set("PID_CONFIG","x_Kp" ,str(app.gui.balancePidWindow.Slider1.get() ) )
        config.set("PID_CONFIG","x_Ki" ,str(app.gui.balancePidWindow.Slider2.get() ) )
        config.set("PID_CONFIG","x_Kd" ,str(app.gui.balancePidWindow.Slider3.get() ) )
        config.set("PID_CONFIG","y_Kp" ,str(app.gui.balancePidWindow.Slider4.get() ) )
        config.set("PID_CONFIG","y_Ki" ,str(app.gui.balancePidWindow.Slider5.get() ) )
        config.set("PID_CONFIG","y_Kd" ,str(app.gui.balancePidWindow.Slider6.get() ) )

        with open(filename, "w") as config_file:
            config.write(config_file)

    def readPIDConfig():

        filename = "config.ini"
        # Reading Data
        config = configparser.ConfigParser()
        config.read(filename)
        app.gui.balancePidWindow.Slider1.set(float(config.get("PID_CONFIG","x_Kp" )))
        app.gui.balancePidWindow.Slider2.set(float(config.get("PID_CONFIG","x_Ki" )))
        app.gui.balancePidWindow.Slider3.set(float(config.get("PID_CONFIG","x_Kd" )))
        app.gui.balancePidWindow.Slider4.set(float(config.get("PID_CONFIG","y_Kp" )))
        app.gui.balancePidWindow.Slider5.set(float(config.get("PID_CONFIG","y_Ki" )))
        app.gui.balancePidWindow.Slider6.set(float(config.get("PID_CONFIG","y_Kd" )))
       

    



class GUICommands:
    def showServoGUI():
        app.gui.balancePidWindow.hide()
        app.gui.servoAngleWindow.show()
        app.gui.bodyMoveWindow.hide()
        app.gui.footPositionWindow.hide()
        app.gui.gaitWindow.hide()

    def showFootGUI():
        app.gui.balancePidWindow.hide()
        app.gui.servoAngleWindow.hide()
        app.gui.bodyMoveWindow.hide()
        app.gui.footPositionWindow.show()
        app.gui.gaitWindow.hide()

    def showBodyGUI():
        app.gui.bodyMoveWindow.show()
        app.gui.balancePidWindow.hide()
        app.gui.servoAngleWindow.hide()
        app.gui.footPositionWindow.hide()
        app.gui.gaitWindow.hide()

    def showBalanceGUI():
        
        app.gui.bodyMoveWindow.hide()
        app.gui.balancePidWindow.show()
        app.gui.servoAngleWindow.hide()
        app.gui.footPositionWindow.hide()
        app.gui.gaitWindow.hide()

    def showGaitGUI():
        
        app.gui.bodyMoveWindow.hide()
        app.gui.balancePidWindow.hide()
        app.gui.servoAngleWindow.hide()
        app.gui.footPositionWindow.hide()
        app.gui.gaitWindow.show()
        

global parentWindow

parentWindow  = tk.Tk()



class YertleApp:
    def __init__(self):
        self.UdpY = YertleUdp()
        self.PidY = YertlePid(self)
        self.SerialY = YertleSerial(self)
        self.gui = GUI(self)
        self.commands = YerlteCommands()
    
        #self.gui.balancePidWindow.show()
        serial_thread = threading.Thread(target=self.SerialY.threadFunction, args=(1,))
        serial_thread.start()
    
        udp_thread = threading.Thread(target=self.UdpY.threadFunction, args=(1,))
        udp_thread.start()
            
        pid_thread = threading.Thread(target=self.PidY.threadFunction, args=(1,))
        pid_thread.start() 

class GUI:
        def __init__(self,parent):
            self.mainWindow = parentWindow
            self.mainWindow.title('Yerlte Debug')
            self.mainWindow.geometry('800x480')
            self.mainWindow.rowconfigure(0)
            self.mainWindow.rowconfigure((1,2,3), weight=1, uniform="123")
            self.mainWindow.columnconfigure(1, weight=1)
            self.mainWindow.columnconfigure(0)
            self.terminalWindow = self.TerminalWindow()
            self.topMenuWindow = self.TopMenuWindow()
            self.bottomMenuWindow = self.BottomMenuWindow()
            self.balancePidWindow = self.BalancePidWindow()
            self.servoAngleWindow = self.ServoAngleWindow()
            self.footPositionWindow = self.FootPositionWindow()
            self.bodyMoveWindow = self.BodyMoveWindow()
            self.portsWindow = self.PortsWindow(parent)
            self.gaitWindow  = self.GaitWindow()

        class TerminalWindow:
            def __init__(self):
                self.txt_edit = tk.Text(parentWindow,bg="black",fg="green")
                self.txt_edit.grid(row=3, column=1, sticky="nsew")
            
            def print(self,data):
                self.txt_edit.insert(tk.END,data + '\n')
                self.txt_edit.see("end")

        class TopMenuWindow:
            def __init__(self):
                super().__init__()
                self.menuWindow = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.menuWindow.rowconfigure((0,1,2,3,4,5),  weight=1,uniform='third')
                self.menuWindow.columnconfigure(0, minsize=200, weight=1)

                self.btn_1 = ttk.Button(self.menuWindow, text="Servo Control",command=GUICommands.showServoGUI)
                self.btn_2 = ttk.Button(self.menuWindow, text="Foot Positions",command=GUICommands.showFootGUI)
                self.btn_3 = ttk.Button(self.menuWindow, text="Body Translation",command=GUICommands.showBodyGUI)

                self.btn_4 = ttk.Button(self.menuWindow, text="Balance PID",command=GUICommands.showBalanceGUI)

                self.btn_7 = ttk.Button(self.menuWindow, text="Gait",command=GUICommands.showGaitGUI)

                self.btn_6 = ttk.Button(self.menuWindow, text="Get PWM Values",command=YerlteCommands.getIsPWMCmd)

                self.btn_1.grid(row=0, column=0,sticky="nsew",padx=5, pady=5)
                self.btn_2.grid(row=1, column=0,sticky="nsew",padx=5, pady=5)
                self.btn_3.grid(row=2, column=0,sticky="nsew",padx=5, pady=5)
                self.btn_4.grid(row=3, column=0,sticky="nsew",padx=5, pady=5)
                self.btn_6.grid(row=5, column=0,sticky="nsew",padx=5, pady=5)
                self.btn_7.grid(row=4, column=0,sticky="nsew",padx=5, pady=5)

                self.menuWindow.grid(row=1, column=0,rowspan=2, sticky="wns")

        class BottomMenuWindow:
            def __init__(self):
                self.bottomMenuWindow = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.bottomMenuWindow.rowconfigure((0,1,2,3),  weight=1,uniform='456')
                self.bottomMenuWindow.columnconfigure((0,1),  weight=1,uniform='875')

                global dataActive 
                dataActive = tk.StringVar() 
                dataActive.set("1")

                self.bbtn_11 = tk.Button(self.bottomMenuWindow, text="Config IMU",command = YerlteCommands.calibrateIMU)
                self.bbtn_11.grid(row=0, column=0,sticky="nsew",padx=5, pady=5,columnspan=2)

                self.bbtn_12 = tk.Button(self.bottomMenuWindow, text="Update IMU Config",command = YerlteCommands.sendIMUCalibrationData)
                self.bbtn_12.grid(row=1, column=0,sticky="nsew",padx=5, pady=5,columnspan=2)

                self.lRBttn = ttk.Radiobutton(self.bottomMenuWindow, text = " Data Active", variable = dataActive,value = "1")
                self.lRBttn.grid(row=2, column=0,sticky="nsew",padx=5, pady=5)

                self.lRBttn2 = ttk.Radiobutton(self.bottomMenuWindow, text = "Data Paused", variable = dataActive,value = "2")
                self.lRBttn2.grid(row=2, column=1,sticky="nsew",padx=5, pady=5)

                self.btn_9 = tk.Button(self.bottomMenuWindow, text="SEND DATA",bg='green',command = YerlteCommands.writeAnglesButton)
                self.btn_9.grid(row=3, column=0,sticky="nsew",padx=5, pady=5,columnspan=2)

                self.btn_10 = tk.Button(self.bottomMenuWindow, text="RESET POS",command = YerlteCommands.ResetCmd)
                self.btn_10.grid(row=4, column=0,sticky="nsew",padx=5, pady=5,columnspan=2)

                self.lRBttn.setvar("1")
                self.bottomMenuWindow.grid(row=3, column=0, sticky="ewns")

        class BalancePidWindow:
            def __init__(self):
                ########### balance  move form
                self.frm_balance = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.frm_balance.rowconfigure((0,1,2,3,4,5),  weight=1,uniform='eqreqer')
                self.frm_balance.columnconfigure((0,1,2,3,4,5),  weight=1,uniform='qwrq4w')

                self.rawX = tk.StringVar()
                self.rawY = tk.StringVar()

                self.outputX = tk.StringVar()
                self.outputY = tk.StringVar()

                self.magTKStringDataX = tk.StringVar()
                self.magTKStringDataY = tk.StringVar()
                self.magTKStringDataZ = tk.StringVar()
                self.accTKStringDataX = tk.StringVar()
                self.accTKStringDataY = tk.StringVar()
                self.accTKStringDataZ = tk.StringVar()
                self.rotTKStringDataX = tk.StringVar()
                self.rotTKStringDataY = tk.StringVar()
                self.rotTKStringDataZ = tk.StringVar()

                ##x
                balanceSlider_labelrotXL = ttk.Label(self.frm_balance,text='IMU X RAW:')
                balanceSlider_labelrotXL.grid(row=0, column=0, sticky="nsew")

                balanceSlider_labelrotX = tk.Label(self.frm_balance,text='0', bg="blue",textvariable=self.rawX)
                balanceSlider_labelrotX.grid(row=0, column=1, sticky="nsew")
                
                ##y
                balanceSlider_labelrotYL = ttk.Label(self.frm_balance,text='IMU Y RAW:')
                balanceSlider_labelrotYL.grid(row=0, column=2, sticky="nsew")

                balanceSlider_labelrotY = tk.Label(self.frm_balance,text='0', bg="blue",textvariable=self.rawY)
                balanceSlider_labelrotY.grid(row=0, column=3, sticky="nsew")




                balanceSlider_labelYLP = ttk.Label(self.frm_balance,text='P:')
                balanceSlider_labelYLP.grid(row=1, column=2, sticky="nsew")

                balanceSlider_labelYLP = ttk.Label(self.frm_balance,text='I:')
                balanceSlider_labelYLP.grid(row=2, column=2, sticky="nsew")

                balanceSlider_labelYLP = ttk.Label(self.frm_balance,text='D:')
                balanceSlider_labelYLP.grid(row=3, column=2, sticky="nsew")
                

                balanceSlider_labelXLP = ttk.Label(self.frm_balance,text='P:')
                balanceSlider_labelXLP.grid(row=1, column=0, sticky="nsew")

                balanceSlider_labelXLP = ttk.Label(self.frm_balance,text='I:')
                balanceSlider_labelXLP.grid(row=2, column=0, sticky="nsew")

                balanceSlider_labelXLP = ttk.Label(self.frm_balance,text='D:')
                balanceSlider_labelXLP.grid(row=3, column=0, sticky="nsew")

                balanceSlider_labelXpid = ttk.Label(self.frm_balance,text='PID out X:')
                balanceSlider_labelXpid.grid(row=4, column=0, sticky="nsew")

                balanceSlider_labelYpid = ttk.Label(self.frm_balance,text='PID out Y:')
                balanceSlider_labelYpid.grid(row=4, column=2, sticky="nsew")


                balanceSlider_labelpidX = tk.Label(self.frm_balance,text='0', bg="blue",textvariable=self.outputX)
                balanceSlider_labelpidX.grid(row=4, column=1, sticky="nsew")

                balanceSlider_labelpidY = tk.Label(self.frm_balance,text='0', bg="blue",textvariable=self.outputY)
                balanceSlider_labelpidY.grid(row=4, column=3, sticky="nsew")

            
                self.Slider1 = tk.Scale(self.frm_balance,from_=0,to=10,orient='horizontal',resolution=0.01)
                self.Slider1.bind("<ButtonRelease-1>",YerlteCommands.modifyPIDvalues)
                self.Slider1.grid(row=1, column=1, sticky="nsew")

                self.Slider2 = tk.Scale(self.frm_balance,from_=0,to=10,orient='horizontal',resolution=0.01)
                self.Slider2.bind("<ButtonRelease-1>",YerlteCommands.modifyPIDvalues)
                self.Slider2.grid(row=2, column=1, sticky="nsew")

                self.Slider3 = tk.Scale(self.frm_balance,from_=0,to=10,orient='horizontal',resolution=0.01)
                self.Slider3.bind("<ButtonRelease-1>",YerlteCommands.modifyPIDvalues)
                self.Slider3.grid(row=3, column=1, sticky="nsew")

                self.Slider4 = tk.Scale(self.frm_balance,from_=0,to=10,orient='horizontal',resolution=0.01)
                self.Slider4.bind("<ButtonRelease-1>",YerlteCommands.modifyPIDvalues)
                self.Slider4.grid(row=1, column=3, sticky="nsew")

                self.Slider5 = tk.Scale(self.frm_balance,from_=0,to=10,orient='horizontal',resolution=0.01)
                self.Slider5.bind("<ButtonRelease-1>",YerlteCommands.modifyPIDvalues)
                self.Slider5.grid(row=2, column=3, sticky="nsew")

                self.Slider6 = tk.Scale(self.frm_balance,from_=0,to=10,orient='horizontal',resolution=0.01)
                self.Slider6.bind("<ButtonRelease-1>",YerlteCommands.modifyPIDvalues)
                self.Slider6.grid(row=3, column=3, sticky="nsew")

                self.bbtn_11 = tk.Button(self.frm_balance, text="Save PID",command = FileCommands.writePIDConfig)
                self.bbtn_11.grid(row=0, column=4,sticky="nsew",padx=5, pady=5,columnspan=2)

                self.bbtn_12 = tk.Button(self.frm_balance, text="Load PID",command = FileCommands.readPIDConfig)
                self.bbtn_12.grid(row=1, column=4,sticky="nsew",padx=5, pady=5,columnspan=2)



            def hide(self):
                self.frm_balance.grid_forget()
            def show(self):
                FileCommands.readPIDConfig()
                self.frm_balance.grid(row=1, column=1,sticky="nsew",rowspan=2)

        class ServoAngleWindow:
            def __init__(self):
                self.frm_servoAngles = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.frm_servoAngles.rowconfigure((0,1,2,3,4,5,6,7),  weight=1,uniform='456')
                self.frm_servoAngles.columnconfigure((0,1),  weight=1,uniform='875')


                self.slider_label1 = ttk.Label(self.frm_servoAngles,text='Left Front Leg Angles:')
                self.slider_label1.grid(row=0, column=0, sticky="nsew")

                self. slider1 = tk.Scale(self.frm_servoAngles,from_=-45,to=45,orient='horizontal',resolution=1)
                self.slider1.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider1.grid(row=1, column=0, sticky="nsew")

                self.slider2 = tk.Scale(self.frm_servoAngles,from_=-90,to=20,orient='horizontal',resolution=1)
                self.slider2.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider2.grid(row=2, column=0, sticky="nsew")

                self. slider3 = tk.Scale(self.frm_servoAngles,from_=13,to=90,orient='horizontal',resolution=1)
                self.slider3.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider3.grid(row=3, column=0, sticky="nsew")



                self.slider_label2 = ttk.Label(self.frm_servoAngles,text='Right Front Leg Angles:',)
                self.slider_label2.grid(row=0, column=1, sticky="nsew")

                self.slider4 = tk.Scale(self.frm_servoAngles,from_=-45,to=45,orient='horizontal',resolution=1)
                self.slider4.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider4.grid(row=1, column=1, sticky="nsew")

                self.slider5 = tk.Scale(self.frm_servoAngles,from_=-90,to=20,orient='horizontal',resolution=1)
                self.slider5.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider5.grid(row=2, column=1, sticky="nsew")

                self.slider6 = tk.Scale(self.frm_servoAngles,from_=13,to=90,orient='horizontal',resolution=1)
                self.slider6.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider6.grid(row=3, column=1, sticky="nsew")


                self.slider_label3 = ttk.Label(self.frm_servoAngles,text='Left Back Leg Angles:')
                self.slider_label3.grid(row=4, column=0, sticky="nsew")

                self.slider7 = tk.Scale(self.frm_servoAngles,from_=-45,to=45,orient='horizontal',resolution=1)
                self.slider7.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider7.grid(row=5, column=0, sticky="nsew")

                self.slider8 = tk.Scale(self.frm_servoAngles,from_=-90,to=20,orient='horizontal',resolution=1)
                self.slider8.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider8.grid(row=6, column=0, sticky="nsew")

                self.slider9 = tk.Scale(self.frm_servoAngles,from_=13,to=90,orient='horizontal',resolution=1)
                self.slider9.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider9.grid(row=7, column=0, sticky="nsew")


                self.slider_label4 = ttk.Label(self.frm_servoAngles,text='Right Back Leg Angles:')
                self.slider_label4.grid(row=4, column=1, sticky="nsew")

                self.slider10 = tk.Scale(self.frm_servoAngles,from_=-45,to=45,orient='horizontal',resolution=1)
                self.slider10.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider10.grid(row=5, column=1, sticky="nsew")

                self.slider11 = tk.Scale(self.frm_servoAngles,from_=-90,to=20,orient='horizontal',resolution=1)
                self.slider11.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider11.grid(row=6, column=1, sticky="nsew")

                self.slider12 = tk.Scale(self.frm_servoAngles,from_=13,to=90,orient='horizontal',resolution=1)
                self.slider12.bind("<ButtonRelease-1>",YerlteCommands.writeAngles)
                self.slider12.grid(row=7, column=1, sticky="nsew")

                #self.frm_servoAngles.grid(row=1, column=1,sticky="nsew",rowspan=2)

            def hide(self):
                self.frm_servoAngles.grid_forget()
            def show(self):
                self.frm_servoAngles.grid(row=1, column=1,sticky="nsew",rowspan=2)

        class FootPositionWindow:
            def __init__(self):
                # foot position form
                self.frm_footPos = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.frm_footPos.rowconfigure((0,1,2,3,4,5,6,7),  weight=1,uniform='456')
                self.frm_footPos.columnconfigure((0,1),  weight=1,uniform='875')


                self.fPosSlider_label1 = ttk.Label(self.frm_footPos,text='Left Front XYZ:')
                self.fPosSlider_label1.grid(row=0, column=0, sticky="nsew")

                self.fPosSlider1 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider1.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider1.grid(row=1, column=0, sticky="nsew")

                self.fPosSlider2 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider2.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider2.grid(row=2, column=0, sticky="nsew")

                self.fPosSlider3 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider3.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider3.grid(row=3, column=0, sticky="nsew")



                self.fPosSlider_label2 = ttk.Label(self.frm_footPos,text='Right Front Leg XYZ:',)
                self.fPosSlider_label2.grid(row=0, column=1, sticky="nsew")

                self.fPosSlider4 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider4.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider4.grid(row=1, column=1, sticky="nsew")

                self.fPosSlider5 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider5.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider5.grid(row=2, column=1, sticky="nsew")

                self.fPosSlider6 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider6.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider6.grid(row=3, column=1, sticky="nsew")




                self.fPosSlider_label3 = ttk.Label(self.frm_footPos,text='Left Back Leg XYZ:')
                self.fPosSlider_label3.grid(row=4, column=0, sticky="nsew")

                self.fPosSlider7 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider7.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider7.grid(row=5, column=0, sticky="nsew")

                self.fPosSlider8 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider8.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider8.grid(row=6, column=0, sticky="nsew")

                self.fPosSlider9 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider9.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider9.grid(row=7, column=0, sticky="nsew")


                self.fPosSlider_label4 = ttk.Label(self.frm_footPos,text='Right Back Leg XYZ:')
                self.fPosSlider_label4.grid(row=4, column=1, sticky="nsew")

                self.fPosSlider10 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider10.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider10.grid(row=5, column=1, sticky="nsew")

                self.fPosSlider11 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider11.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider11.grid(row=6, column=1, sticky="nsew")

                self.fPosSlider12 = tk.Scale(self.frm_footPos,from_=-15,to=15,orient='horizontal',resolution=1)
                self.fPosSlider12.bind("<ButtonRelease-1>",YerlteCommands.writeFootPosition)
                self.fPosSlider12.grid(row=7, column=1, sticky="nsew")

            def hide(self):
                self.frm_footPos.grid_forget()
            def show(self):
                self.frm_footPos.grid(row=1, column=1,sticky="nsew",rowspan=2)

        class BodyMoveWindow:
            def __init__(self):
                # Body move form
                self.frm_bodyMove = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.frm_bodyMove.rowconfigure((0,1,2,3,4,5,6,7),  weight=1,uniform='456')
                self.frm_bodyMove.columnconfigure((0,1),  weight=1,uniform='875')


                self.bMoveSlider_label1 = ttk.Label(self.frm_bodyMove,text='Body Translation XYZ:')
                self.bMoveSlider_label1.grid(row=0, column=0, sticky="nsew")

                self.bMoveSlider1 = tk.Scale(self.frm_bodyMove,from_=-5,to=5,orient='horizontal',resolution=1)
                #bMoveSlider1.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider1.grid(row=1, column=0, sticky="nsew")

                self.bMoveSlider2 = tk.Scale(self.frm_bodyMove,from_=-5,to=7,orient='horizontal',resolution=1)
                #bMoveSlider2.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider2.grid(row=2, column=0, sticky="nsew")

                self.bMoveSlider3 = tk.Scale(self.frm_bodyMove,from_=-5,to=5,orient='horizontal',resolution=1)
                #bMoveSlider3.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider3.grid(row=3, column=0, sticky="nsew")



                self.bMoveSlider_label2 = ttk.Label(self.frm_bodyMove,text='Body Rotation XYZ :',)
                self.bMoveSlider_label2.grid(row=0, column=1, sticky="nsew")

                self.bMoveSlider4 = tk.Scale(self.frm_bodyMove,from_=-10,to=10,orient='horizontal',resolution=1)
                #bMoveSlider4.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider4.grid(row=1, column=1, sticky="nsew")

                self.bMoveSlider5 = tk.Scale(self.frm_bodyMove,from_=-10,to=10,orient='horizontal',resolution=1)
                ##bMoveSlider5.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider5.grid(row=2, column=1, sticky="nsew")

                self.bMoveSlider6 = tk.Scale(self.frm_bodyMove,from_=-30,to=30,orient='horizontal',resolution=1)
                #bMoveSlider6.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider6.grid(row=3, column=1, sticky="nsew")
            
            def hide(self):
                self.frm_bodyMove.grid_forget()
            def show(self):
                self.frm_bodyMove.grid(row=1, column=1,sticky="nsew",rowspan=2)

        class GaitWindow:
            def __init__(self):
                # Body move form
                self.frm_gait = tk.Frame(parentWindow, relief=tk.RAISED, bd=1)
                self.frm_gait.rowconfigure((0,1,2,3,4,5,6,7),  weight=1,uniform='456')
                self.frm_gait.columnconfigure((0,1),  weight=1,uniform='875')



                self.Slider1 = tk.Scale(self.frm_gait,from_=0,to=100,orient='horizontal',resolution=0.1)
                #bMoveSlider1.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.Slider1.grid(row=0, column=0, sticky="nsew")

                self.label1 = ttk.Label(self.frm_gait,text='Speed')
                self.label1.grid(row=1, column=0, sticky="nsew")

                self.Slider2 = tk.Scale(self.frm_gait,from_=0,to=5,orient='horizontal',resolution=1)
                #bMoveSlider2.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.Slider2.grid(row=2, column=0, sticky="nsew")

                self.label2 = ttk.Label(self.frm_gait,text='Foot Elevation')
                self.label2.grid(row=3, column=0, sticky="nsew")


                self.Slider3 = tk.Scale(self.frm_gait,from_=0,to=5,orient='horizontal',resolution=1)
                #bMoveSlider3.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.Slider3.grid(row=4, column=0, sticky="nsew")

                self.label3 = ttk.Label(self.frm_gait,text='Stride')
                self.label3.grid(row=5, column=0, sticky="nsew")

                self.Slider4 = tk.Scale(self.frm_gait,from_=0,to=5,orient='horizontal',resolution=1)
                #bMoveSlider3.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.Slider4.grid(row=6, column=0, sticky="nsew")

                self.label4 = ttk.Label(self.frm_gait,text='Stride')
                self.label4.grid(row=7, column=0, sticky="nsew")



                self.bMoveSlider_label2 = ttk.Label(self.frm_gait,text='Body Rotation XYZ :',)
                self.bMoveSlider_label2.grid(row=0, column=1, sticky="nsew")

                self.bMoveSlider4 = tk.Scale(self.frm_gait,from_=-10,to=10,orient='horizontal',resolution=1)
                #bMoveSlider4.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider4.grid(row=1, column=1, sticky="nsew")

                self.bMoveSlider5 = tk.Scale(self.frm_gait,from_=-10,to=10,orient='horizontal',resolution=1)
                ##bMoveSlider5.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider5.grid(row=2, column=1, sticky="nsew")

                self.bMoveSlider6 = tk.Scale(self.frm_gait,from_=-30,to=30,orient='horizontal',resolution=1)
                #bMoveSlider6.bind("<ButtonRelease-1>",animateBodyTranslation)
                self.bMoveSlider6.grid(row=3, column=1, sticky="nsew")
            
            def hide(self):
                self.frm_gait.grid_forget()
            def show(self):
                self.frm_gait.grid(row=1, column=1,sticky="nsew",rowspan=2)

        class PortsWindow:
            def __init__(self,parent):
                self.parent = parent
                self.ports = serial.tools.list_ports.comports()
                #port dropdown menu
                self.port = tk.StringVar()
                self.port.set(str(self.ports[0]))

                self.portsMenu = tk.OptionMenu(parentWindow, self.port, *self.ports, command = self.initComPort())
                self.portsMenu.config(width=15)
                self.portsMenu.grid(row=0, column=0,sticky="nsew")

            #start com port function
            def initComPort(self):
                index1 = self.search(self.ports,self.port.get())
                currentPort = str(self.ports[index1])
                comPortVar = str(currentPort.split(' ')[0])
                self.parent.SerialY.serialObj.port = comPortVar
                self.parent.SerialY.serialObj.baudrate = 115200
                self.parent.SerialY.serialObj.open()
            #search
            def search(self,list, platform):
                for i in range(len(list)):
                    if str(list[i]).strip(' ') == str(platform).strip(' '):
                        return i
                    return 99

class YerlteCommands:
    #send angles over serial data
    def writeAnglesButton():
        output = "a "#+str(slider1.get())+" "+str(slider2.get())+" "+str(slider3.get())+" "+str(slider4.get())+" "+str(slider5.get())+" "+str(slider6.get())+" "+str(slider7.get())+" "+str(slider8.get())+" "+str(slider9.get())+" "+str(slider10.get())+" "+str(slider11.get())+" "+str(slider12.get())+ "\n"
        if dataActive.get()== "1":
            app.SerialY.writeSerial(output)
            app.UdpY.send(output)             
    def writeAngles(self,a):
        YerlteCommands.writeAnglesButton()
        
    #send feet positions over serial data
    def writeFootPositionButton():
        output ="f "#+str(fPosSlider1.get())+" "+str(fPosSlider2.get())+" "+str(fPosSlider3.get())+" "+str(fPosSlider4.get())+" "+str(fPosSlider5.get())+" "+str(fPosSlider6.get())+" "+str(fPosSlider7.get())+" "+str(fPosSlider8.get())+" "+str(fPosSlider9.get())+" "+str(fPosSlider10.get())+" "+str(fPosSlider11.get())+" "+str(fPosSlider12.get())+ "\n"
        if dataActive.get()== "1":
            app.SerialY.writeSerial(output)
            app.UdpY.send(output)

    def writeFootPosition(a):
        YerlteCommands.writeFootPositionButton()
    
    def getIsPWMCmd():
        output = "p\n"
        if dataActive.get()== "1":
            app.SerialY.writeSerial(output)
            app.UdpY.send(output) 
    
    def calibrateIMU():
        output = "c\n"
        app.SerialY.writeSerial(output)
        app.UdpY.send(output)
    
    def ResetCmd():
        slider1.set(0)
        slider2.set(0)
        slider3.set(0)
        slider4.set(0)
        slider5.set(0)
        slider6.set(0)
        slider7.set(0)
        slider8.set(0)
        slider9.set(0)
        slider10.set(0)
        slider11.set(0)
        slider12.set(0)
        
        fPosSlider1.set(0)
        fPosSlider2.set(0)
        fPosSlider3.set(0)
        fPosSlider4.set(0)
        fPosSlider5.set(0)
        fPosSlider6.set(0)
        fPosSlider7.set(0)
        fPosSlider8.set(0)
        fPosSlider9.set(0)
        fPosSlider10.set(0)
        fPosSlider11.set(0)
        fPosSlider12.set(0)
        bMoveSlider1.set(0)
        bMoveSlider2.set(0)
        bMoveSlider3.set(0)
        bMoveSlider4.set(0)
        bMoveSlider5.set(0)
        bMoveSlider6.set(0)
        output = "d\n"
        SerialY.writeSerial(output)
        UDPClientSocket.sendto(output.encode(),serverAddressPort ) 
        if serialObj.isOpen()and serialObj.in_waiting ==False:
            serialObj.write(("d\n").encode())
    
    def sendIMUCalibrationData():
        FileCommands.readIMUConfig()
        output =("C "       +str(magXbias) +" "
                            +str(magYbias) +" "
                            +str(magZbias) +" "
                            +str(rotXbias) +" "
                            +str(rotYbias) +" "
                            +str(rotZbias) +" "
                            +str(accXbias) +" "
                            +str(accYbias) +" "
                            +str(accZbias) +" "
                            +str(magXscale)+" "
                            +str(magYscale)+" "
                            +str(magZscale)+" dasdas \n")
        app.SerialY.writeSerial(output)
        app.UdpY.send(output) 

    def modifyPIDvalues(a):
        YerlteCommands.modifyPID()
    
    def modifyPID():
        app.PidY.ImuPidX.Kp = app.gui.balancePidWindow.Slider1.get()
        app.PidY.ImuPidX.Ki = app.gui.balancePidWindow.Slider2.get()
        app.PidY.ImuPidX.Kd = app.gui.balancePidWindow.Slider3.get()

        app.PidY.ImuPidY.Kp = app.gui.balancePidWindow.Slider4.get()
        app.PidY.ImuPidY.Ki = app.gui.balancePidWindow.Slider5.get()
        app.PidY.ImuPidY.Kd = app.gui.balancePidWindow.Slider6.get()


        #app.PidY.ImuPidX.Ki ( float(val1) , float(val2) , float(val3) )
        #app.PidY.ImuPidY.tunings( float(val4) , float(val5) , float(val))

class YertleUdp:
        def __init__(self):
            self.UDP_IP = "10.0.0.88" # The IP that is printed in the serial monitor from the ESP32
            self.UDPFromAddress = 0 # (UDP_IP, 49713)
            self.SHARED_UDP_PORT = 1234
            self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UdpY
            self.UDPServerSocket.bind(("10.0.0.13", self.SHARED_UDP_PORT)) # Internet  # UdpY
            self.serverAddressPort   = (self.UDP_IP, 24321)
            self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        

        def loop(self):
            ready = select.select([self.UDPServerSocket], [], [], 0.1)
            if ready[0]:        
                self.data, self.UDPFromAddress = self.UDPServerSocket.recvfrom(1024)
                try:        
                    self.checkForData()
                except UnicodeDecodeError:
                    print("decode error")
        
        def checkForData(self):
            global magDataX, magDataY, magDataZ,accDataX, accDataY, accDataZ,rotDataX, rotDataY, rotDataZ
            global magXbias, magYbias, magZbias, rotXbias, rotYbias, rotZbias, accXbias, accYbias, accZbias, magXscale, magYscale, magZscale
            decodedData = self.data.decode()
            if(decodedData[0] == 'm'):
                dataList  = self.data.split()
                magDataX = dataList[1]
                magDataY = dataList[2]
                magDataZ = dataList[3]

            elif(decodedData[0] == 'a'):
                dataList  = self.data.split()
                accDataX = dataList[1]
                accDataY = dataList[2]
                accDataZ = dataList[3]
            elif(decodedData[0] == 'r'):
                dataList  = self.data.split()
                rotDataX = dataList[1].decode()
                rotDataY = dataList[2].decode()
                rotDataZ = dataList[3].decode()
            
            elif(decodedData[0] == 'c'):
                dataList  = self.data.split()

                magXbias = dataList[1].decode()
                magYbias = dataList[2].decode()
                magZbias = dataList[3].decode()
                
                rotXbias = dataList[1].decode()
                rotYbias = dataList[2].decode()
                rotZbias = dataList[3].decode()

                accXbias = dataList[1].decode()
                accYbias = dataList[2].decode()
                accZbias = dataList[3].decode()
                
                magXscale = dataList[1].decode()
                magYscale = dataList[2].decode()
                magZscale = dataList[3].decode()

                FileCommands.writeIMUConfig()
            else:
                app.gui.terminalWindow.print(self.data.decode())

        def threadFunction(self,input):
            while True:
                self.loop()

        def send(self,data):
            self.UDPClientSocket.sendto(data.encode(),self.serverAddressPort)

class YertlePid:
        def __init__(self,parent):
            self.parent = parent
            self.ImuPidX = PID(1, 0.1, 0.05)
            self.ImuPidY = PID(1, 0.1, 0.05)
            self.moveCount = 0
            self.lf_gaitOffset =  [0,0,0]
            self.rf_gaitOffset =  [0,0,0]
            self.lb_gaitOffset =  [0,0,0]
            self.rb_gaitOffset =  [0,0,0]


        def gaitCalc(self,time):

            self.lf_gaitOffset[1] =  clamp(- self.parent.gui.gaitWindow.Slider2.get()*math.sin(math.radians(time)),-self.parent.gui.gaitWindow.Slider2.get(),0)
            self.rf_gaitOffset[1] =  clamp(  self.parent.gui.gaitWindow.Slider2.get()*math.sin(math.radians(time)),-self.parent.gui.gaitWindow.Slider2.get(),0)
            self.lb_gaitOffset[1] =  clamp(  self.parent.gui.gaitWindow.Slider2.get()*math.sin(math.radians(time)),-self.parent.gui.gaitWindow.Slider2.get(),0)
            self.rb_gaitOffset[1] =  clamp(- self.parent.gui.gaitWindow.Slider2.get()*math.sin(math.radians(time)),-self.parent.gui.gaitWindow.Slider2.get(),0)

            
        def threadFunction(self,input):
            
            
            self.ImuPidX.tunings = (0.23, 0.01, 0.0)
            self.ImuPidX.output_limits = (-45, 45)
            
            self.ImuPidY.tunings = (0.3, 0, 0.0)
            self.ImuPidY.output_limits = (-35, 35)

            while True:
                if (self.moveCount >=360):
                    self.moveCount = 0
                else:
                    self.moveCount = self.moveCount + self.parent.gui.gaitWindow.Slider1.get()
                self.gaitCalc(self.moveCount)

                self.parent.gui.balancePidWindow.rawX.set(rotDataZ)
                self.parent.gui.balancePidWindow.rawY.set(rotDataY)
                
                xval = round(self.ImuPidX(float(rotDataZ)),2)
                yval = round(self.ImuPidY(float(rotDataY)),2)

                #xval =clamp(xval,-30,30)

                self.writeBodyTranslationTick(0,-yval,-xval)
                self.parent.gui.balancePidWindow.outputX.set(round(xval,1))
                self.parent.gui.balancePidWindow.outputY.set(round(yval,1))
                time.sleep(0.025)

        def writeBodyTranslationTick(self,thetaX,thetaY,thetaZ):
            x =  0
            y =  -0.5
            z =  0
            bodyLength = 23
            bodyWidth = 10

            lf_x =  x - ((15+y) * math.sin(thetaY * math.pi / 180)) + self.lf_gaitOffset[0]
            lf_y =  y + (0.5 * bodyWidth * math.tan(thetaZ* math.pi / 180)) + (0.5 * bodyLength * math.tan(thetaY* math.pi / 180)) - (0.5 * bodyWidth * math.tan(thetaX* math.pi / 180))  + self.lf_gaitOffset[1]
            lf_z =  z - ((15+y) * math.sin(thetaZ * math.pi / 180)) + ((15+y) * math.sin(thetaX * math.pi / 180))  + self.lf_gaitOffset[2]

            rf_x =  x - ((15+y) * math.sin(thetaY * math.pi / 180)) + self.rf_gaitOffset[0]
            rf_y =  y - (0.5 * bodyWidth * math.tan(thetaZ* math.pi / 180)) + (0.5 * bodyLength * math.tan(thetaY* math.pi / 180)) + (0.5 * bodyWidth * math.tan(thetaX* math.pi / 180))  + self.rf_gaitOffset[1]
            rf_z =  z - ((15+y) * math.sin(thetaZ * math.pi / 180)) + ((15+y) * math.sin(thetaX * math.pi / 180))  + self.rf_gaitOffset[2]

            lb_x =  x - ((15+y) * math.sin(thetaY * math.pi / 180)) + self.lb_gaitOffset[0]
            lb_y =   y + (0.5 * bodyWidth * math.tan(thetaZ* math.pi / 180)) - (0.5 * bodyLength * math.tan(thetaY* math.pi / 180)) + (0.5 * bodyWidth * math.tan(thetaX* math.pi / 180))   + self.lb_gaitOffset[1]
            lb_z =  z - ((15+y) * math.sin(thetaZ * math.pi / 180)) - ((15+y) * math.sin(thetaX * math.pi / 180))  + self.lb_gaitOffset[2]

            rb_x =  x - ((15+y) * math.sin(thetaY * math.pi / 180)) + self.rb_gaitOffset[0]
            rb_y =  y - (0.5 * bodyWidth * math.tan(thetaZ* math.pi / 180)) - (0.5 * bodyLength * math.tan(thetaY* math.pi / 180)) - (0.5 * bodyWidth * math.tan(thetaX* math.pi / 180)) + self.rb_gaitOffset[1]
            rb_z =  z - ((15+y) * math.sin(thetaZ * math.pi / 180)) - ((15+y) * math.sin(thetaX * math.pi / 180))  + self.rb_gaitOffset[2]
            output =("f "   +str(round(lf_x,1))+" "
                            +str(round(lf_y,1))+" "
                            +str(round(lf_z,1))+" "
                            +str(round(rf_x,1))+" "
                            +str(round(rf_y,1))+" "
                            +str(round(rf_z,1))+" "
                            +str(round(lb_x,1))+" "
                            +str(round(lb_y,1))+" "
                            +str(round(lb_z,1))+" "
                            +str(round(rb_x,1))+" "
                            +str(round(rb_y,1))+" "
                            +str(round(rb_z,1))+" dasdas \n")

            if dataActive.get()== "1":
                self.parent.SerialY.writeSerial(output)
                self.parent.UdpY.send(output) 

class YertleSerial:
        def __init__(self,parent):
            self.parent = parent
            self.serialObj = serial.Serial(write_timeout = 0,timeout = 0)

        def threadFunction(self,input):
            while True:
                self.checkSerialPort()

            #Check serial port
        def checkSerialPort(self):
            if self.serialObj.isOpen() and self.serialObj.in_waiting:
                recentPacket = self.serialObj.readline()
                recentPacketString = recentPacket.decode('utf').rstrip('\n')
                self.parent.gui.terminalWindow.print(recentPacketString)

        #send serial data
        def writeSerial(self,inputString):
            if self.serialObj.isOpen()and self.serialObj.in_waiting ==False:
                self.serialObj.write(inputString.encode())

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)



if __name__ == "__main__":
    global app
    app = YertleApp()
    app.gui.mainWindow.mainloop()
        



    



