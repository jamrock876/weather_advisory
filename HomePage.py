__author__ = 'TheLazySavant'
__doc__ = """grace weather advisory v1.0
          project uses OpenWeatherMap api to collect data for the following five day forecast
          each day is mapped with a correct weather image signifying the weather conditions for that day
          the user will be able to send notifications to its employees in a database about conditions that day if
          their credentials(usern & password) have the rights. A generic email is set up with the group of
          employees selected which can be altered to the users liking.
          TO-DO/BUGS: fix screen resizing abilities
                implement the keep me logged in button
                compare login credentials against a database instead of it being hardwired in the program
                pass subject parameter to the message set up based on the day selected to notify this includes the date as well
                convert print statements to logs based on information needed to help debug
                fix menu capabilities
          NOTE: since tkinter buttons are platform independent, buttons on home page are assumed to be flat and seemless
                which is not the case on mac
          REQUIREMENTS: user will need python 3, tkinter, urllib, mysql.connector(for python in native os)
          """

from tkinter import *
from urllib import request
import tkinter.messagebox
import tkinter.scrolledtext as tkst
import json
import time, datetime
import smtplib
import mysql.connector
from mysql.connector import errorcode



openWeatherWebpage = "http://api.openweathermap.org/data/2.5/weather?q="
openWeatherWebpage5dayforcast = "http://api.openweathermap.org/data/2.5/forecast?q="
appid = "&appid=xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

class HomePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.controller = controller
        self.width = 700
        self.height = 700
        self.leftscrollday = 0
        self.rightscrollday = 0
        self.loading = PhotoImage(file='./res/weather images/progress_bar1.gif')
        self.sunny = PhotoImage(file='./res/weather images/SunnyT.gif')
        self.mostlycloudy = PhotoImage(file='./res/weather images/MostlyCloudyT.gif')
        self.partlycloudy = PhotoImage(file='./res/weather images/PartlyCloudyT.gif')
        self.hazy = PhotoImage(file='./res/weather images/HazyT.gif')
        self.cloudy = PhotoImage(file='./res/weather images/CloudyT.gif')
        self.mostlysunny = PhotoImage(file='./res/weather images/MostlySunnyT.gif')
        self.rain = PhotoImage(file='./res/weather images/RainT.gif')
        self.thunderstorm = PhotoImage(file='./res/weather images/ThunderstormT.gif')

        # center/bottom canvas
        self.middlecanv = Canvas(self, height=800, width=700, bg='#33495f')
        self.middlecanv.place(relx=0, rely=0, anchor=CENTER)
        self.middlecanv.grid(row=1, column=1)
        self.leftcanvas = Canvas(self.middlecanv, width=260, height=500, bd=0, highlightthickness=0)
        self.rightcanvas = Canvas(self.middlecanv, width=260, height=500, bd=0, highlightthickness=0)

        '''
        # MenuBar
        self.gk_menu = Menu(self)
        self.master.config(menu=self.gk_menu)
        self.gk_subMenu = Menu(self.gk_menu)
        self.gk_menu.add_cascade(label="About", menu=self.gk_subMenu)
        self.gk_subMenu.add_command(label="About Us", command=self.companyInfo)
        '''

        # ALL Canvas
        # Banner Canvas
        self.banner = Canvas(self, width=700, height=200)
        self.banner.grid(row=0, column=0, columnspan=3)
        self.banner_photo = PhotoImage(file='./res/GraceKennedyBanner.gif')
        self.banner.create_image(75,0, image=self.banner_photo, anchor='nw')

        # Left Canvas
        self.displayforcastformontegobay(0)
        self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')

        # ARROW BUTTONS
        self.leftimage = PhotoImage(file="./res/backarrowicon.gif")
        self.leftarrow = Button(self, image=self.leftimage, command=lambda: self.leftscrollfolder('left'), bg='#33495f', borderwidth=0, highlightthickness=0)
        self.leftcanvas.create_window(1, 250, anchor='w', window=self.leftarrow)
        self.rightimage = PhotoImage(file="./res/backarrowicon1.gif")
        self.rightarrow = Button(self, image=self.rightimage, command=lambda: self.leftscrollfolder('right'), bg='#33495f', borderwidth=0, highlightthickness=0)
        self.leftcanvas.create_window(230, 250, anchor='w', window=self.rightarrow)

        # FULL INFO AND NOTIFY BUTTON
        self.mobay_Button = Button(self, text="Full Info", command=self.displayMobayWeather, anchor='nw')
        self.advisem_button = Button(self, text="Notify", command=lambda: self.controller.show_frame(Emailservicepage), anchor='nw')
        self.advisem_button.configure(width=10, activebackground="#33495f", relief=FLAT) #line doesnt show configurations on mac, cuz its not supported
        self.mobay_Button.configure(width=10, activebackground="#33495f", relief=FLAT) #line doesnt show configurations on mac, cuz its not supported
        self.leftcanvas.create_window(10, 460, anchor='w', window=self.mobay_Button)
        self.leftcanvas.create_window(140, 460, anchor='w', window=self.advisem_button)

        # ---------------------------------------Right Canvas--------------------------------------------
        self.displayforcaseforkingston(0)
        self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')

        # ARROW BUTTONS(saved memory by not importing the same buttons again)
        self.leftarrow = Button(self, image=self.leftimage, command=lambda: self.rightscrollfolder('left') , bg='#33495f', borderwidth=0, highlightthickness=0)
        self.rightcanvas.create_window(1, 250, anchor='w', window=self.leftarrow)
        self.rightarrow = Button(self, image=self.rightimage, command=lambda: self.rightscrollfolder('right'), bg='#33495f', borderwidth=0, highlightthickness=0)
        self.rightcanvas.create_window(230, 250, anchor='w', window=self.rightarrow)

        # FULL INFO AND NOTIFY BUTTON
        self.advisek_button = Button(self, text='Notify', command=lambda: self.controller.show_frame(Emailservicepage), anchor='nw')
        self.kingston_Button = Button(self, text="Full Info", command=self.displayKingstonWeather)
        self.advisek_button.configure(width = 10, activebackground = "#33B5E5", relief = FLAT) #line doesnt show configurations on mac, cuz its not supported
        self.kingston_Button.configure(width = 10, activebackground = "#33B5E5", relief = FLAT) #line doesnt show configurations on mac, cuz its not supported
        self.rightcanvas.create_window(10, 460, anchor='w', window=self.kingston_Button)
        self.rightcanvas.create_window(140, 460, anchor='w', window=self.advisek_button)

        # APPLY BOTH CANVAS TO A STATIC LOCATION
        self.middlecanv.create_window(85,260, anchor='w', window=self.leftcanvas)
        self.middlecanv.create_window(380,260, anchor='w', window=self.rightcanvas)

    def companyInfo(self):
        tkinter.messagebox.showinfo("About Us", "Application developed for Grace Kennedy Ltd\nby Trevaughn Daley\nBrooklyn College '15")

    def displayMobayWeather(self):
        response = request.urlopen("http://api.openweathermap.org/data/2.5/forecast?q=Montego%20Bay,jm&mode=json"+appid)
        body = response.read().decode('utf-8')
        data = json.loads(body)
        tkinter.messagebox.showinfo("Full Info", "Weather code: " + str(self.data['list'][self.leftscrollday]['weather'][0]['id']) +
        "\n\n" + "City: " + str(self.data['city']['name']) +
        "\n\n" + "Temperature: " + str(((self.data['list'][self.leftscrollday]['main']['temp']-273.15)*1.800)+32) + " °F" +
        "\n\n" + "Humidity: " + str(self.data['list'][self.leftscrollday]['main']['humidity']) + " %" +
        "\n\n" + "Pressure: " + str(self.data['list'][self.leftscrollday]['main']['pressure']) + " hPa" +
        "\n\n" + "Cloud: " + str(self.data['list'][self.leftscrollday]['clouds']['all']) + " %" +
        "\n\n" + "Wind speed: " + str(self.data['list'][self.leftscrollday]['wind']['speed']) + " mps")

    def displayKingstonWeather(self):
        response = request.urlopen("http://api.openweathermap.org/data/2.5/forecast?q=Kingston,jm&mode=json"+appid)
        body = response.read().decode('utf-8')
        # print(body)
        data = json.loads(body)
        # print(data)
        tkinter.messagebox.showinfo("Full Info", "Weather code: " + str(self.data['list'][self.rightscrollday]['weather'][0]['id']) +
        "\n\n" + "City: " + str(self.data['city']['name']) +
        "\n\n" + "Temperature: " + str(((self.data['list'][self.rightscrollday]['main']['temp']-273.15)*1.800)+32) + " °F" +
        "\n\n" + "Humidity: " + str(self.data['list'][self.rightscrollday]['main']['humidity']) + " %" +
        "\n\n" + "Pressure: " + str(self.data['list'][self.rightscrollday]['main']['pressure']) + " hPa" +
        "\n\n" + "Cloud: " + str(self.data['list'][self.rightscrollday]['clouds']['all']) + " %" +
        "\n\n" + "Wind speed: " + str(self.data['list'][self.rightscrollday]['wind']['speed']) + " mps")

    def displayforcastformontegobay(self, index):
        self.response = request.urlopen("http://api.openweathermap.org/data/2.5/forecast?q=Montego%20Bay,jm&mode=json"+appid)
        self.body = self.response.read().decode('utf-8')
        self.data = json.loads(self.body)
        self.indicies = self.locatetwelveindicies()
        self.id = str(self.data['list'][index]['weather'][0]['id'])
        print("Weather code: " + str(self.data['list'][index]['weather'][0]['id']))
        print("City: " + str(self.data['city']['name']))
        print("Temperature: " + str(((self.data['list'][index]['main']['temp']-273.15)*1.800)+32) + " °F")
        print("Humidity: " + str(self.data['list'][index]['main']['humidity']) + " %")
        print("Pressure: " + str(self.data['list'][index]['main']['pressure']) + " hPa")
        print("Cloud: " + str(self.data['list'][index]['clouds']['all']) + " %")
        print("Wind speed: " + str(self.data['list'][index]['wind']['speed']) + " mps")
        try:
            print("Rainfall : " + str(self.data['list'][index]['rain']['3h']) + " mm")
        except:
            print("Rainfall : NO RAINFALL")
            print("")
        self.codemap(self.id, 'mobay')
        self.displaydate()

    def leftscrollfolder(self, direction):
        # NAVIGATE
        if direction == 'left':
            print('left button was clicked')
            self.leftscrollday -= 1
        if direction == 'right':
            print('right button was clicked')
            self.leftscrollday += 1

        # control the circular rotation or the left panel
        if self.leftscrollday == 5:
            self.leftscrollday = 0
        if self.leftscrollday == -1:
            self.leftscrollday = 4

        # REPRESENT ACTUAL 5 DAY FORECAST
        if self.leftscrollday == 0:
            self.displayforcastformontegobay(0)
        elif self.leftscrollday == 1:
            self.displayforcastformontegobay(1)
        elif self.leftscrollday == 2:
            self.displayforcastformontegobay(2)
        elif self.leftscrollday == 3:
            self.displayforcastformontegobay(3)
        elif self.leftscrollday == 4:
            self.displayforcastformontegobay(4)

    def rightscrollfolder(self, direction):
        # NAVIGATE
        if direction == 'left':
            print('left button was clicked')
            self.rightscrollday -= 1
        if direction == 'right':
            print('right button was clicked')
            self.rightscrollday += 1

        # control the circular rotation or the left panel
        if self.rightscrollday == 5:
            self.rightscrollday = 0
        if self.rightscrollday == -1:
            self.rightscrollday = 4

        # REPRESENT ACTUAL 5 DAY FORECAST
        if self.rightscrollday == 0:
            self.displayforcaseforkingston(0)
        elif self.rightscrollday == 1:
            self.displayforcaseforkingston(1)
        elif self.rightscrollday == 2:
            self.displayforcaseforkingston(2)
        elif self.rightscrollday == 3:
            self.displayforcaseforkingston(3)
        elif self.rightscrollday == 4:
            self.displayforcaseforkingston(4)

    def codemap(self, code, side):
        print(code + " side: " + side)
        #   THUNDERSTORM
        if code == '200' or code == '201' or code == '202' or code == '210' or code == '211' or code == '212' or code == '221' or code == '230' or code == '231' or code == '232':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.thunderstorm, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.thunderstorm, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        #   DRIZZLE
        if code == '300' or code == '301' or code == '302' or code == '310' or code == '311' or code == '312' or code == '313' or code == '314' or code == '321':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.rain, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.rain, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        #   RAIN
        if code == '500' or code == '501' or code == '502' or code == '503' or code == '504' or code == '511' or code == '520' or code == '521' or code == '522' or code == '531':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.rain, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.rain, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        #   ATMOSPHERE
        if code == '701' or code == '711' or code == '721' or code == '731' or code == '741' or code == '751' or code == '761' or code == '762' or code == '771' or code == '781':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.hazy, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.hazy, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        #   CLOUDS
        if code == '800':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.sunny, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            elif side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.sunny, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        if code == '801':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.partlycloudy, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.partlycloudy, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        if code == '802' or code == '803':
            print("hello")
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.mostlycloudy, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.mostlycloudy, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        if code == '804':
            if side == 'mobay':
                print("bay")
                self.leftcanvas.create_image(0,0, image=self.cloudy, anchor='nw')
                self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
            if side == 'kingston':
                print("town")
                self.rightcanvas.create_image(0,0, image=self.cloudy, anchor='nw')
                self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')
        #   Extreme need to create image for extreme
        # if code == '900' or code == '901' or code == '902' or code == '903' or code == '904' or code == '905' or code == '906':
        #     if side == 'mobay':
        #         print("bay")
        #         self.leftcanvas.create_image(0,0, image=self.extreme, anchor='nw')
        #         self.leftcanvas.create_text(50,10, text='Montego Bay', anchor='nw', font=('copperplate',25), fill='white')
        #     if side == 'kingston':
        #         print("town")
        #         self.rightcanvas.create_image(0,0, image=self.extreme, anchor='nw')
        #         self.rightcanvas.create_text(80,10, text='Kingston', anchor='nw', font=('copperplate',25), fill='white')

    def displayforcaseforkingston(self, index):
        self.response = request.urlopen("http://api.openweathermap.org/data/2.5/forecast?q=Kingston,jm&mode=json"+appid)
        self.body = self.response.read().decode('utf-8')
        self.data = json.loads(self.body)
        self.indicies = self.locatetwelveindicies()
        self.id = str(self.data['list'][index]['weather'][0]['id'])
        print("City: " + str(self.data['city']['name']))
        print("Weather code: " + str(self.data['list'][index]['weather'][0]['id']))
        print("Temperature: " + str(((self.data['list'][index]['main']['temp']-273.15)*1.800)+32) + " °F")
        print("Humidity: " + str(self.data['list'][index]['main']['humidity']) + " %")
        print("Pressure: " + str(self.data['list'][index]['main']['pressure']) + " hPa")
        print("Cloud: " + str(self.data['list'][index]['clouds']['all']) + " %")
        print("Wind speed: " + str(self.data['list'][index]['wind']['speed']) + " mps")
        try:
            print("Rainfall : " + str(self.data['list'][index]['rain']['3h']) + " mm")
        except:
            print("Rainfall : NO RAINFALL")
        print("")
        self.codemap(self.id, 'kingston')
        self.displaydate()

    # since api give us time we have to locate which json index will give us 12pm data set for further processing
    def locatetwelveindicies(self):
        count = 0
        it = 0
        self.middayforcast = []
        while count < 5:
            if str(self.data['list'][it]['dt_txt']).endswith("12:00:00"):
                self.middayforcast.append(it)
                count += 1
            it+=1
            # print(it)
        return self.middayforcast

    def giftedweather(self):
        self.newWindow = Toplevel(self)
        self.app = self.emailservicepage(self.newWindow)

    def displaydate(self):
        if self.leftscrollday == 0:
            day0 = datetime.date.today()
            self.leftcanvas.create_text(60,400, text=str(day0.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.leftscrollday == 1:
            day1 = datetime.date.today() + datetime.timedelta(days=1)
            self.leftcanvas.create_text(60,400, text=str(day1.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.leftscrollday == 2:
            day2 = datetime.date.today() + datetime.timedelta(days=2)
            self.leftcanvas.create_text(60,400, text=str(day2.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.leftscrollday == 3:
            day3 = datetime.date.today() + datetime.timedelta(days=3)
            self.leftcanvas.create_text(60,400, text=str(day3.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.leftscrollday == 4:
            day4 = datetime.date.today() + datetime.timedelta(days=4)
            self.leftcanvas.create_text(60,400, text=str(day4.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.rightscrollday == 0:
            day0 = datetime.date.today()
            self.rightcanvas.create_text(60,400, text=str(day0.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.rightscrollday == 1:
            day1 = datetime.date.today() + datetime.timedelta(days=1)
            self.rightcanvas.create_text(60,400, text=str(day1.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.rightscrollday == 2:
            day2 = datetime.date.today() + datetime.timedelta(days=2)
            self.rightcanvas.create_text(60,400, text=str(day2.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.rightscrollday == 3:
            day3 = datetime.date.today() + datetime.timedelta(days=3)
            self.rightcanvas.create_text(60,400, text=str(day3.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')
        if self.rightscrollday == 4:
            day4 = datetime.date.today() + datetime.timedelta(days=4)
            self.rightcanvas.create_text(60,400, text=str(day4.strftime("%A")), anchor='nw', font=('copperplate',25), fill='white')

class Emailservicepage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.mailinglist = []
        self.default_to = StringVar()
        self.default_from = StringVar()
        self.default_subject = StringVar()
        self.width = 700
        self.height = 700

        # ALL Canvas
        self.width = 700
        self.height = 700
        # Banner Canvas
        self.banner = Canvas(self, width=700, height=200)
        self.banner.grid(row=0, column=0)
        self.banner_photo = PhotoImage(file='./res/GraceKennedyBanner.gif')
        self.banner.create_image(75,0, image=self.banner_photo, anchor='nw')

        # select employeees
        self.clerk_var = IntVar()
        self.engineer_var = IntVar()
        self.it_var = IntVar()
        self.manager_var = IntVar()
        self.sales_var = IntVar()

        # select staff members to email
        self.mid = Frame(self, width=700, height=400, bd=4, relief='groove')
        self.selection_instruction = Label(self.mid, text='Select the role of employees you would like to send email not'
                                                          'ifications:', fg='red').grid(row=0, column=1, sticky='ew')
        self.select_clerk = Checkbutton(self.mid, text='Clerk', variable=self.clerk_var).grid(row=1, column=0, sticky='w')
        self.select_engineer = Checkbutton(self.mid, text='Engineer', variable=self.engineer_var).grid(row=2, column=0, sticky='w')
        self.select_it = Checkbutton(self.mid, text='IT', variable=self.it_var).grid(row=3, column=0, sticky='w')
        self.select_manager = Checkbutton(self.mid, text='Manager', variable=self.manager_var).grid(row=4, column=0, sticky='w')
        self.select_sales = Checkbutton(self.mid, text='Sales', variable=self.sales_var).grid(row=5, column=0, sticky='w')
        self.mid.grid(row=1, column=0, sticky='nsew', ipady=130)

        # next cancel buttom
        self.bottom = Canvas(self, width=700, height=100, bd=2, highlightthickness=2, highlightcolor='black')
        self.bottom.grid(row=2, column=0, sticky='e', pady=10)

        self.cancelButton = Button(self.bottom, text='Cancel', command=lambda: self.controller.show_frame(HomePage)).grid(row=0, column=3, sticky='w')
        self.nextButton = Button(self.bottom, text='Next', command=self.maillogin).grid(row=0, column=4, sticky='w')

        response = request.urlopen(openWeatherWebpage + "Kingston,jm"+appid)
        body = response.read().decode('utf-8')
        # print(body)
        data = json.loads(body)

    def updatelists(self):
        mandb = ManDatabase()

        # process selected values
        if self.clerk_var.get() == 1:
            # print('clerk selected')
            self.templ = mandb.get_all_clerks()
            for s in self.templ:
                self.mailinglist.append(s)
        if self.engineer_var.get() == 1:
            # print("engineer selected")
            self.templ = mandb.get_all_clerks()
            for s in self.templ:
                self.mailinglist.append(s)
        if self.it_var.get() == 1:
            # print("IT selected")
            self.templ = mandb.get_all_clerks()
            for s in self.templ:
                self.mailinglist.append(s)
        if self.manager_var.get() == 1:
            # print("Manager selected")
            self.templ = mandb.get_all_clerks()
            for s in self.templ:
                self.mailinglist.append(s)
        if self.sales_var.get() == 1:
            # print("Sales selected")
            self.templ = mandb.get_all_clerks()
            for s in self.templ:
                self.mailinglist.append(s)
        if self.sales_var.get() != 1 and self.manager_var.get() != 1 and self.it_var.get() != 1 and self.engineer_var.get() != 1 and self.clerk_var.get() != 1:
            tkinter.messagebox.showwarning('No Selected Staff', 'Please note no selected staff selected. You may have to manually edit the "TO:" field')
            # print('nothing was selected ')

        self.default_to.set(', '.join(self.mailinglist))

    def maillogin(self):
        self.updatelists()
        self.newWindow = Toplevel(self)
        self.app = MailLoginPortal(self.newWindow, self.controller, self.default_to.get())

class Emailservicepage2(Frame):
    def __init__(self, parent, controller, to, email, password):
        Frame.__init__(self, parent)
        # file setup and manip
        self.email = open('RainDelay.txt', 'r')
        self.CURRENTDATE = time.strftime("%A, %B %d %Y")
        self.processfile()

        # varables for the entry fields which have to be stringvar
        self.default_to = StringVar()
        self.default_from = StringVar()
        self.default_subject = StringVar()
        self.default_to.set(to)
        self.default_from.set(email)
        self.default_subject.set("Tomorrow's schedule")
        self.password = password

        # declatarions/initialization for window/frame
        self.controller = controller
        self.width = 700
        self.height = 700

        # ALL Canvas
        self.width = 700
        self.height = 700
        # Banner Canvas
        self.banner = Canvas(self, width=700, height=200)
        self.banner.grid(row=0, column=0)
        self.banner_photo = PhotoImage(file='./res/GraceKennedyBanner.gif')
        self.banner.create_image(75,0, image=self.banner_photo, anchor='nw')

        self.mid = Frame(self, width=700, height=400, bd=4, relief='groove')
        self.emailcanvas = Canvas(self, width=700, height=400, bd=20, highlightthickness=2, highlightcolor='black', bg='#33495f')
        self.emailcanvas.grid(row=1, column=0, sticky='w')

        self.to_label = Label(self.emailcanvas, text="TO:", bg='#33495f').grid(row=0, column=0, sticky='e')
        self.from_label = Label(self.emailcanvas, text="FROM:", bg='#33495f').grid(row=1, column=0, sticky='e')
        self.subject_label = Label(self.emailcanvas, text="SUBJECT:", bg='#33495f').grid(row=2, column=0, sticky='e')
        self.to_entry = Entry(self.emailcanvas, width=70, textvariable=self.default_to).grid(row=0, column=1, pady=2)
        self.from_entry = Entry(self.emailcanvas, width=70, textvariable=self.default_from).grid(row=1, column=1, pady=2)
        self.subject_entry = Entry(self.emailcanvas, width=70, text=self.default_subject).grid(row=2, column=1, pady=2)

        self.defaultemail = tkst.ScrolledText(self.emailcanvas, wrap=WORD, width=94, height=19)
        self.defaultemail.grid(padx=10, pady=10, row=3, column=0, sticky='e', columnspan=2)
        self.defaultemail.insert(INSERT, self.getbody())

        # bottom canvas
        self.bottom = Canvas(self, width=700, height=100, bd=2, highlightthickness=2, highlightcolor='black', bg='#33495f')
        self.bottom.grid(row=2, column=0, sticky='e', pady=10)

        self.backButton = Button(self.bottom, text='Back', command=lambda: self.controller.show_frame(Emailservicepage)).grid(row=0, column=3, sticky='w')
        self.sendButton = Button(self.bottom, text='Send', command=self.delivermail).grid(row=0, column=4, sticky='w')

    def processfile(self):
        f = ''
        global GENEMAIL                             #this looks like just using the keyword global ive globalized the variable
        for line in self.email.readlines():
            f += line
        f = f.replace('FULLDATE', self.CURRENTDATE)
        GENEMAIL = f
        self.email.close()
        return GENEMAIL

    def getbody(self):
        return GENEMAIL

    def delivermail(self):
        self.mail = ManMail(self.default_from.get(), self.password, self.default_to.get(), self.getbody(), self.default_subject.get())
        self.mail.connect_to_gmail()
        self.mail.sendemail()
        self.mail.close_gmail_connection()

class ManMail:
    """
    class is tailored to use gmail as a means or sending email.(its smtp is configured for gmail only)
    in the future more webservices would be added to accommodate a broader audience
    """
    def __init__(self, email, password, to, body, subject):
        # GMAIL Credentials
        self.gmail_sender = email
        self.gmail_password = password
        self.TO = to
        self.BODY = body
        self.SUBJECT = subject

    # connect to gmail services
    def connect_to_gmail(self):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.gmail_sender, self.gmail_password)

    def sendemail(self):
        self.BODY = '\r\n'.join([
            'SUBJECT: %s' % self.SUBJECT,
            '',
            'BODY: %s' % self.BODY
            ])
        try:
            self.server.sendmail(self.gmail_sender, [self.TO], self.BODY)
            print('Email successfully sent')
            tkinter.messagebox._show("message sent", "message successfully sent")
        except:
            print('Error sending email')
            tkinter.messagebox.showerror("Error", "message could not me sent\nplease double check credentials or settings on gmail account")

    def close_gmail_connection(self):
        self.server.quit()

class ManDatabase:
    """
    Sample data can be found in text files given
    In attempt to access a database. user may have to alter this class slightly to grab and change data in their own
    customized database. First start by updating credentials then use queries tailored to your table. Mine is
    CREATE TABLE GraceKennedyEmployees (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    telephone VARCHAR(255),
    role VARCHAR(30),
    email VARCHAR(30));
    """
    def __init__(self):
        try:
            self.con = mysql.connector.connect(user='xxxxxxxxxx', password='xxxxxxxxxx', host='xxxxxxxxxx', database='xxxxxxxxx')
            self.myCursor = self.con.cursor()
            print("successfully connected to DB")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    # need to use try blocks
    def insertIntoEmployees(self):
        self.index = 0
        for i in self.populationCensus.firstName:
            bundled = "'"+self.populationCensus.firstName[self.index]+"', '"+self.populationCensus.lastName[self.index]+"', '"+self.populationCensus.addressList[self.index]+"', '"+self.populationCensus.cityList[self.index]+"', '"+self.populationCensus.countryList[self.index]+"', '"+self.populationCensus.phoneNumberList[self.index]+"', '"+self.populationCensus.roleList[self.index]+"', '"+self.populationCensus.emailList[self.index]+"'"
            str = "INSERT INTO GraceKennedyEmployees(firstName, lastName, address, city, country, telephone, role, email) VALUES("+bundled+")"
            self.myCursor.execute(str)
            self.index += 1
        print("Succesfull")

    def doCommit(self):
        # Make sure data is committed to the database
        self.con.commit()

    def addheads(self):
        self.myCursor.execute(self.add_employee, self.data_employee)
        self.myCursor.execute(self.add_employee1)

    def closeconnection(self):
        self.myCursor.close()
        self.con.close()

    def get_all_clerks(self):
        self.clerkslist = []
        try:
            self.statement = """SELECT email FROM test.GraceKennedyEmployees WHERE role = 'Clerk'"""
            self.myCursor.execute(self.statement)
            self.rows = self.myCursor.fetchall()

            print('Total Row(s):', self.myCursor.rowcount)
            for row in self.rows:
                self.clerkslist.append(''.join(row))
        except mysql.connector.Error as err:
            print(err)
        return self.clerkslist

    def get_all_engineers(self):
        self.engineerlist = []
        try:
            self.statement = """SELECT email FROM test.GraceKennedyEmployees WHERE role = 'Engineer'"""
            self.myCursor.execute(self.statement)
            self.rows = self.myCursor.fetchall()

            print('Total Row(s):', self.myCursor.rowcount)
            for row in self.rows:
                self.engineerlist.append(''.join(row))
        except mysql.connector.Error as err:
            print(err)
        return self.engineerlist

    def get_all_it(self):
        self.itlist = []
        try:
            self.statement = """SELECT email FROM test.GraceKennedyEmployees WHERE role = 'IT'"""
            self.myCursor.execute(self.statement)
            self.rows = self.myCursor.fetchall()

            print('Total Row(s):', self.myCursor.rowcount)
            for row in self.rows:
                self.itlist.append(''.join(row))
        except mysql.connector.Error as err:
            print(err)
        return self.itlist

    def get_all_managers(self):
        self.managerlist = []
        try:
            self.statement = """SELECT email FROM test.GraceKennedyEmployees WHERE role = 'Manager'"""
            self.myCursor.execute(self.statement)
            self.rows = self.myCursor.fetchall()

            print('Total Row(s):', self.myCursor.rowcount)
            for row in self.rows:
                self.managerlist.append(''.join(row))
        except mysql.connector.Error as err:
            print(err)
        return self.managerlist

    def get_all_sales(self):
        self.saleslist = []
        try:
            self.statement = """SELECT email FROM test.GraceKennedyEmployees WHERE role = 'Sales'"""
            self.myCursor.execute(self.statement)
            self.rows = self.myCursor.fetchall()

            print('Total Row(s):', self.myCursor.rowcount)
            for row in self.rows:
                self.saleslist.append(''.join(row))
        except mysql.connector.Error as err:
            print(err)
        return self.saleslist


class MailLoginPortal(Frame):
    """
    Validates uses credentials

    ToDo: add username and password to privilege employees table and query if username and password matched that which is entered.
    for the time being we assume only one employee is considered privileged and his/her credentials are hard coded in the email_val and password_val
    fields.
    """
    def __init__(self, master, controller, to):
        self.to = to
        self.email_val = "<username>@gmail.com"
        self.password_val = "<password>"
        self.controller = controller

        self.master = master #from main im passing the actual tk as master i.e root
        self.cv = Canvas(self.master, width=200, height=130)
        self.cv.pack(side=LEFT, fill='both', expand='yes')
        self.photo = PhotoImage(file="./res/gracelogo.gif")
        self.cv.create_image(10, 10, image=self.photo, anchor='nw')

        self.fields = Canvas(self.master, width=150, height=80, bd=0, highlightthickness=0)
        self.fields.pack(side=LEFT, expand=NO)
        self.eMail = Label(self.fields, text="Email: ")
        self.password = Label(self.fields, text="Password: ")
        self.eMailField = Entry(self.fields)
        self.passwordField = Entry(self.fields, show="*")

        self.c = Checkbutton(self.fields, text="Keep me logged in")

        self.cancel_button = Button(self.fields, text='Cancel', command=self.close_windows)
        self.login_button = Button(self.fields, text='Login', command=self.login)

        self.eMail.grid(row=1, sticky=E)
        self.password.grid(row=2, sticky=E)
        self.eMailField.grid(row=1, column=1)
        self.passwordField.grid(row=2, column=1)
        self.c.grid(row=3, columnspan=2)
        self.cancel_button.grid(row=4, column=1, sticky='w')
        self.login_button.grid(row=4, column=1, sticky='e')

        # Flow management
        self.eMailField.bind("<Return>", self.emailfunc)
        self.passwordField.bind("<Return>", self.passwordfunc)
        self.eMailField.focus()

    def emailfunc(self, event):
        self.eMailField.get()
        self.passwordField.focus()

    def passwordfunc(self, event):
        print(self.passwordField.get())

    def close_windows(self):
        self.master.destroy()

    def login(self):
        global user_email, user_password
        user_email = self.eMailField.get()
        user_password = self.passwordField.get()
        if self.validate(user_email, user_password):
            self.close_windows()
            self.controller.addnewframe(self.to, user_email, user_password)
            self.controller.show_frame(Emailservicepage2)
        else:
            self.incorrectcredentials = Label(self.fields, text='***Incorrect Username or Password***', font=('ariel', 12), fg='red').grid(row=0, column=0, columnspan=4)

    def validate(self, email, password):
        if email == self.email_val and password == self.password_val:
            print("SUCCESSFULL!")
            return True
        else:
            print("Incorrect Password")
            return False

class PageManager(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.container = Frame(self)
        self.container.grid(row=1, column=1)

         # dictionary containing all the frames
        self.frames = {}

        for F in (HomePage, Emailservicepage):

            frame = F(self.container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def addnewframe(self, to, email, password):
        frame = Emailservicepage2(self.container, self, to, email, password)

        self.frames[Emailservicepage2] = frame

        frame.grid(row=0, column=0, sticky="nsew")

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

if __name__ == '__main__':
    # print(__doc__)
    app = PageManager()
    app.mainloop()