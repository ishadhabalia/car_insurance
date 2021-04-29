#------------------------imports---------------------------#
import math
import tkinter as tk
from tkinter import *
import tkinter.ttk
from tkinter import messagebox
import mysql.connector
import time
import re
import uuid
from datetime import datetime  
from datetime import timedelta  
from datetime import date
from dateutil.relativedelta import *
from fpdf import FPDF

#---------------------database-------------------------------------#
mydb = mysql.connector.connect(
  host="localhost",
  user="root_temp",
  password="root@123",
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS User")
mycursor.execute("use User")

mycursor.execute("Create table if not exists userdata(username VARCHAR(30) NOT NULL PRIMARY KEY,password VARCHAR(30),name VARCHAR(255),  email varchar(100) unique)")

#userdata table
mycursor.execute("Create table if not exists policy(username VARCHAR(30) NOT NULL,policy_id varchar(7) NOT NULL PRIMARY KEY,gender enum('Male','Female'), age tinyint unsigned, reg_year INT UNSIGNED,city enum('Mumbai','Pune','Nagpur','Aurangabad','Nashik'),cc_capacity INT UNSIGNED,price INT UNSIGNED, date_of_policy date,installment enum('Yearly','Half-yearly','Quaterly'),damage enum('Self','Third Party','Both'),premium float,FOREIGN KEY (username) REFERENCES userdata(username),self float,thirdparty float)")

#genderfactor table
mycursor.execute("Create table if not exists genderfactor(gender enum('Male','Female') NOT NULL PRIMARY KEY,factor float(5,4))")
query = "INSERT IGNORE INTO genderfactor (gender, factor) VALUES (%s, %s)"
val = [
  ('Male', 0.002),
  ('Female', 0.0015),
]
mycursor.executemany(query, val)

#cityfactor table
mycursor.execute("Create table if not exists cityfactor(city enum('Mumbai','Pune','Nagpur','Aurangabad','Nashik') NOT NULL PRIMARY KEY,factor float(5,4))")
query = "INSERT IGNORE INTO cityfactor (city, factor) VALUES (%s, %s)"
val = [
  ('Mumbai', 0.004),
  ('Pune', 0.0035),
  ('Nagpur', 0.003),
  ('Aurangabad', 0.0025),
  ('Nashik', 0.002),
]
mycursor.executemany(query, val)

#agefactor table
mycursor.execute("Create table if not exists agefactor(age_range_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,min TINYINT UNSIGNED NOT NULL UNIQUE,max TINYINT UNSIGNED NOT NULL UNIQUE,factor float(5,4))")
query = "INSERT IGNORE INTO agefactor (min,max, factor) VALUES (%s,%s, %s)"
val = [
  (20,39, 0.002),
  (40,59, 0.0015),
  (60,99, 0.003),
]
mycursor.executemany(query, val)

#yearfactor table
mycursor.execute("Create table if not exists yearfactor(year_range_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,min INT UNSIGNED NOT NULL UNIQUE,max INT UNSIGNED NOT NULL UNIQUE,factor float(5,4))")
query = "INSERT IGNORE INTO yearfactor (min,max, factor) VALUES (%s,%s, %s)"
val = [
  (2013,2016, 0.003),
  (2017,2019, 0.002),
  (2020,2021, 0.001),
]
mycursor.executemany(query, val)

#capacityfactor table
mycursor.execute("Create table if not exists capacityfactor(cc_range_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,min INT UNSIGNED NOT NULL UNIQUE,max INT UNSIGNED NOT NULL UNIQUE,factor float(5,4))")
query = "INSERT IGNORE INTO capacityfactor (min,max, factor) VALUES (%s,%s, %s)"
val = [
  (800,999, 0.001),
  (1000,1199, 0.002),
  (1200,1300, 0.003),
]
mycursor.executemany(query, val)

#pricefactor table
mycursor.execute("Create table if not exists pricefactor(price_range_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,min INT UNSIGNED NOT NULL UNIQUE,max INT UNSIGNED NOT NULL UNIQUE,factor float(5,4))")
query = "INSERT IGNORE INTO pricefactor (min,max, factor) VALUES (%s,%s, %s)"
val = [
  (500000,999999 , 0.001),
  (1000000,1999999, 0.002),
  (2000000 ,9999999 , 0.003),
]
mycursor.executemany(query, val)

mydb.commit()


def main():
    win=Tk()
    app=Login_Window(win)
    win.mainloop()

#------------------------First window-Login/Register---------------------------------
class Login_Window:
    def __init__(self,root):
        
        
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("Login")
        self.root.iconbitmap("icon.ico")
       
        self.var_loguser=StringVar()
        self.var_logpass=StringVar()

        login_frame=LabelFrame(self.root,text="Sign in into your account",padx=30,pady=30,bd=5)
        login_frame.place(relx=0.5, rely=0.3, anchor=CENTER)

        usernamelabel=Label(login_frame,text="Username")  
        usernamelabel.grid(row=0,column=0,pady=20)
        self.userentry=Entry(login_frame,width=35,borderwidth=5,textvariable=self.var_loguser)
        self.userentry.grid(row=0,column=1)

        passwordlabel=Label(login_frame,text="Password")  
        passwordlabel.grid(row=1,column=0,pady=20)
        self.passentry=Entry(login_frame,width=35,borderwidth=5,textvariable=self.var_logpass)
        self.passentry.grid(row=1,column=1)
        self.passentry.config(show="*")

        button_login=Button(login_frame,text="Login",command=self.login)
        button_login.grid(row=2,column=0,pady=20,columnspan=2)

        logreg_frame=LabelFrame(self.root,text="Register",padx=30,pady=30,bd=5)
        logreg_frame.place(relx=0.5, rely=0.65, anchor=CENTER)

        logreg_text = Label(logreg_frame, text="Don't have account! Register by clicking the button")
        logreg_text.grid(row=0,column=0,pady=20)

        button_logreg=Button(logreg_frame,text="Register",command=self.register_new_window)
        button_logreg.grid(row=1,column=0,columnspan=2)

        button_exit=Button(self.root,text="Exit Application",command=self.exit_app)
        button_exit.grid(row=2,column=0,columnspan=2)


    def exit_app(self):
      msgbox=messagebox.askquestion("Exit Application","Do you want to exit application")
      if msgbox=='yes':
        global username
        username=''
        self.root.destroy()

    def register_new_window(self):
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Register(self.root) 
      self.root.mainloop()

    #login function 
    def login(self):
               
        global username
        if self.userentry.get()=="" or self.passentry.get()=="":
            messagebox.showerror("Error","All fields required")
        else:
            query =("SELECT * FROM userdata WHERE username = %s")
            value=(self.var_loguser.get(),)
            mycursor.execute(query,value)
            row1=mycursor.fetchone()
            query =("SELECT * FROM userdata WHERE username = %s and password=%s")
            value=(self.var_loguser.get(),self.var_logpass.get(),)
            mycursor.execute(query,value)
            row2=mycursor.fetchone()
            if row1 == None:
                messagebox.showerror('Invalid', "Username does not exist. Either register or sign in again")  
            elif row2 !=None:
                messagebox.showinfo('Success', "You have signed in successfully")
                username=self.var_loguser.get()
                self.login_success()
                    
            else:
                messagebox.showerror('Invalid', "Invalid Credentials") 
    
    #opens profile window on success
    def login_success(self):
      
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Profile(self.root) 
      self.root.mainloop()

#-------------------------------Registration window-------------------------------#  
class Register:
    def __init__(self,root):
        
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("Register")
        self.root.iconbitmap("icon.ico")

        
        self.var_name=StringVar()
        self.var_email=StringVar()
        self.var_username=StringVar()
        self.var_pass=StringVar()
        self.var_confpass=StringVar()
    
        register_frame=LabelFrame(self.root,text="Register",padx=30,pady=30,bd=5)
        register_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        namelabel=Label(register_frame,text="Full Name")
        namelabel.grid(row=0,column=0,pady=10)
        self.nameentry=Entry(register_frame,width=35,borderwidth=5,textvariable=self.var_name)
        self.nameentry.grid(row=0,column=1)

        emaillabel=Label(register_frame,text="Email ID")
        emaillabel.grid(row=1,column=0,pady=10)
        self.emailentry=Entry(register_frame,width=35,borderwidth=5,textvariable=self.var_email)
        self.emailentry.grid(row=1,column=1)

        regusernamelabel=Label(register_frame,text="Username")  
        regusernamelabel.grid(row=2,column=0,pady=10)
        self.reguserentry=Entry(register_frame,width=35,borderwidth=5,textvariable=self.var_username)
        self.reguserentry.grid(row=2,column=1)

        validpass_frame=Frame(register_frame,padx=10,pady=10,bd=2)
        validpass_frame.grid(row=3,column=1)

        vp_text = Label(validpass_frame, text="Valid Password includes:")
        vp_text.grid(row=0,column=1)
        vp1_text = Label(validpass_frame, text="At least 1 letter between a-z")
        vp1_text.grid(row=1,column=1)
        vp2_text = Label(validpass_frame, text="At least 1 letter between A-Z")
        vp2_text.grid(row=2,column=1)
        vp3_text = Label(validpass_frame, text="At least 1 number between 0-9")
        vp3_text.grid(row=3,column=1)
        vp4_text = Label(validpass_frame, text="At least 1 character from $#@")
        vp4_text.grid(row=4,column=1)
        vp5_text = Label(validpass_frame, text="At least 1 letter between a-z")
        vp5_text.grid(row=5,column=1)
        vp6_text = Label(validpass_frame, text="Minimum length of password should be 8 and maximum 15")
        vp6_text.grid(row=6,column=1)

        regpasswordlabel=Label(register_frame,text="Password")  
        regpasswordlabel.grid(row=4,column=0,pady=10)
        self.regpassentry=Entry(register_frame,width=35,borderwidth=5,textvariable=self.var_pass)
        self.regpassentry.grid(row=4,column=1)
        self.regpassentry.config(show="*")

        conpasswordlabel=Label(register_frame,text="Confirm Password")  
        conpasswordlabel.grid(row=5,column=0,pady=10)
        self.conpassentry=Entry(register_frame,width=35,borderwidth=5,textvariable=self.var_confpass)
        self.conpassentry.grid(row=5,column=1,pady=20)
        self.conpassentry.config(show="*")

        button_reg=Button(register_frame,text="Register",command=self.register_data)
        button_reg.grid(row=6,column=1,pady=10)
       

        button_reglogin=Button(register_frame,text="Login",command=self.login_new_window)
        button_reglogin.grid(row=7,column=1)
        
    
    def clear(self):
      self.var_name.set('')
      self.var_email.set('')
      self.var_username.set('')
      self.var_pass.set('')
      self.var_confpass.set('')
    
    #checks if password is valid
    def validatepass(self):
      flag = 0
      while True:
            
        if (len(self.var_pass.get())<8 or len(self.var_pass.get())>15):
            flag=-1    
            break
                
        elif not re.search("[0-9]", self.var_pass.get()):   
            flag=-1
            break
        elif not re.search("[a-z]", self.var_pass.get()): 
               
            flag = -1
            break
        elif not re.search("[A-Z]",self.var_pass.get()):
                
            flag = -1
            break
        elif not re.search("[$#@]", self.var_pass.get()): 
                
            flag = -1
            break
                
        else:
            flag=0
            break
      return flag
    
    #opens login window
    def login_new_window(self):
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Login_Window(self.root) 
      self.root.mainloop()
      
    def register_data(self):
      exp=r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?" #email validation
      if self.var_name.get()=="" or self.var_email.get()==""  or self.var_username.get()=="" or self.var_pass.get()=="" or self.var_confpass.get()=="":
        messagebox.showerror("Error","All fields required")
      elif self.var_pass.get()!=self.var_confpass.get():
        messagebox.showerror("Error","Passord and Confirm Password should match")
      elif (re.match(exp,self.var_email.get())==None):
        messagebox.showerror("Error","Enter a valid email address")
      
      elif(self.validatepass()==-1):
        messagebox.showerror("Error","Enter a password satifying all rules")

      else:
        #add data to table userdata
        query=('select * from userdata where username=%s')
        value=(self.var_username.get(),)
        mycursor.execute(query,value)
        row1=mycursor.fetchone()
        query=('select * from userdata where email=%s')
        value=(self.var_email.get(),)
        mycursor.execute(query,value)
        row2=mycursor.fetchone()
        if row1!=None:
          messagebox.showerror("Error","Username taken")
        elif row2!=None:
          messagebox.showerror("Error","User already exists! Please enter another email")
        else:
          mycursor.execute("insert into userdata values(%s,%s,%s,%s)",(self.var_username.get(),
                                                                             self.var_pass.get(),
                                                                             self.var_name.get(),
                                                                             self.var_email.get(),
                                                                            #  self.var_gender.get(),
                                                                            #  self.var_age,
                                                                            ))
          mydb.commit()
          messagebox.showinfo("Success","Registered Successfully! Now you can login to your account.")
          self.clear()

#--------------------------Profile window-------------------------------#
class Profile():
  def __init__(self,root):
        
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("User Information")
        self.root.iconbitmap("icon.ico")
        
        query="Select * from userdata where %s=username"
        user=(username,)
        mycursor.execute(query,user)
        userinfo = mycursor.fetchone()
        
        info_frame=LabelFrame(self.root,text="",padx=30,pady=30,bd=5)
        info_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        usernamelabel=Label( info_frame,text="Username: ")
        usernamelabel.grid(row=0,column=0,pady=10)
        usernamedata=Label( info_frame,text=username)
        usernamedata.grid(row=0,column=1,pady=10)


        namelabel=Label( info_frame,text="Name: ")
        namelabel.grid(row=1,column=0,pady=10)
        namedata=Label( info_frame,text=userinfo[2])
        namedata.grid(row=1,column=1,pady=10)


        emaillabel=Label( info_frame,text="Email: ")
        emaillabel.grid(row=2,column=0,pady=10)
        emaildata=Label( info_frame,text=userinfo[3])
        emaildata.grid(row=2,column=1,pady=10)

        button_view=Button(info_frame,text="View Policies",command=self.check_policy)
        button_view.grid(row=4,column=1,pady=10)
      
        button_buy=Button(info_frame,text="Buy Policy",command=self.buy_window)
        button_buy.grid(row=5,column=1)

        button_logout=Button(info_frame,text="Logout",command=self.logout)
        button_logout.grid(row=6,column=1)
  
  #checks is user has any policies
  def check_policy(self):
    query =("SELECT * FROM policy WHERE username = %s")
    value=(username,)
    mycursor.execute(query,value)
    policyinfo=mycursor.fetchall()
    count=len(policyinfo)
    if count==0:
        messagebox.showinfo("No Policies","You have not purchased any policies!")
    else:
      self.view_window()

  #opens window to buy policy
  def buy_window(self):
    self.root.destroy() # close the current window
    self.root = Tk() # create another Tk instance
    self.app = Buy_Policy(self.root) 
    self.root.mainloop()
  
  #opens window to view user's policies
  def  view_window(self):
    self.root.destroy() # close the current window
    self.root = Tk() # create another Tk instance
    self.app = View_Policies(self.root) 
    self.root.mainloop()
  
  def logout(self):
      global username
      username=''
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Login_Window(self.root) 
      self.root.mainloop()

#--------------------Window to view the policies user has------------------#
class View_Policies:
  def __init__(self,root):
        
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("View Policies")
        self.root.iconbitmap("icon.ico")
        
        main_frame=Frame(root)
        main_frame.pack(fill=BOTH,expand=1)
        my_canvas=Canvas(main_frame)
        my_canvas.pack(side=LEFT,fill=BOTH,expand=1)
        my_scrollbar=Scrollbar(main_frame,orient=VERTICAL,command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT,fill=Y)
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>',lambda e:my_canvas.configure(scrollregion=my_canvas.bbox("all")))
        second_frame=Frame(my_canvas)
        my_canvas.create_window((0,0),window=second_frame,anchor="nw")
        query="Select * from userdata where %s=username"
        user=(username,)
        mycursor.execute(query,user)
        userinfo = mycursor.fetchone()
        query =("SELECT * FROM policy WHERE username = %s")
        value=(username,)
        mycursor.execute(query,value)
        policyinfo=mycursor.fetchall()
        count=len(policyinfo)
        
        for i in range(count):
          viewdetails_frame=LabelFrame(second_frame,text="",padx=10,pady=30,bd=5)
          viewdetails_frame.grid(row=i,column=0)
          policyidlabel=Label(viewdetails_frame,text="Policy ID: ")
          policyidlabel.grid(row=0,column=0,pady=10)
          policyiddata=Label( viewdetails_frame,text=policyinfo[i][1])
          policyiddata.grid(row=0,column=1,pady=10)

          #Personal Details
          personallabel=Label( viewdetails_frame,text="Personal Details")
          personallabel.grid(row=1,column=0,pady=10,columnspan=2)
          namelabel=Label( viewdetails_frame,text="Name: ")
          namelabel.grid(row=2,column=0,pady=10)
          namedata=Label( viewdetails_frame,text=userinfo[2])
          namedata.grid(row=2,column=1,pady=10)
          genderlabel=Label( viewdetails_frame,text="Gender: ")
          genderlabel.grid(row=3,column=0,pady=10)
          genderdata=Label(viewdetails_frame,text=policyinfo[i][2])
          genderdata.grid(row=3,column=1,pady=10)
          agelabel=Label( viewdetails_frame,text="Age: ")
          agelabel.grid(row=4,column=0,pady=10)
          agedata=Label( viewdetails_frame,text=policyinfo[i][3])
          agedata.grid(row=4,column=1,pady=10)
      
        #Car details
          carlabel=Label( viewdetails_frame,text="Car Details")
          carlabel.grid(row=5,column=0,pady=10,columnspan=2)
          yearlabel=Label( viewdetails_frame,text="Year of registration: ")
          yearlabel.grid(row=6,column=0,pady=10)
          yeardata=Label( viewdetails_frame,text=policyinfo[i][4])
          yeardata.grid(row=6,column=1,pady=10)
          citylabel=Label( viewdetails_frame,text="City: ")
          citylabel.grid(row=7,column=0,pady=10)
          citydata=Label(viewdetails_frame,text=policyinfo[i][5])
          citydata.grid(row=7,column=1,pady=10)
          pricelabel=Label( viewdetails_frame,text="Price: ")
          pricelabel.grid(row=8,column=0,pady=10)
          pricedata=Label( viewdetails_frame,text=policyinfo[i][7])
          pricedata.grid(row=8,column=1,pady=10)
          caplabel=Label(viewdetails_frame,text="Capacity(in cc): ")
          caplabel.grid(row=9,column=0,pady=10)
          capdata=Label(viewdetails_frame,text=policyinfo[i][6])
          capdata.grid(row=9,column=1,pady=10)

        #Insurance Details
          inslabel=Label( viewdetails_frame,text="Insurance Details")
          inslabel.grid(row=10,column=0,pady=10,columnspan=2)
          
          damagelabel=Label( viewdetails_frame,text="Type of damage: ")
          damagelabel.grid(row=11,column=0,pady=10)
          damagedata=Label( viewdetails_frame,text=policyinfo[i][10])
          damagedata.grid(row=11,column=1,pady=10)
          installlabel=Label(viewdetails_frame,text="Premium installment type: ")
          installlabel.grid(row=12,column=0,pady=10)
          installdata=Label( viewdetails_frame,text=policyinfo[i][9])
          installdata.grid(row=12,column=1,pady=10)
          datelabel=Label( viewdetails_frame,text="Date of Policy: ")
          datelabel.grid(row=13,column=0,pady=10)
          datedata=Label( viewdetails_frame,text=policyinfo[i][8])
          datedata.grid(row=13,column=1,pady=10)

          premiumlabel=Label( viewdetails_frame,text="Premium : ")
          premiumlabel.grid(row=14,column=0,pady=10)
          premiumdata=Label( viewdetails_frame,text=policyinfo[i][11])
          premiumdata.grid(row=14,column=1,pady=10)
       
          startdate=policyinfo[i][8]+ timedelta(days=7)
          
          #generating table for insurance schedule
          if policyinfo[i][9]=='Yearly':
            startdate=startdate.strftime("%d-%m-%Y")
            lst = [('','1'),
           ('Cost',policyinfo[i][11]),
           ('Date',startdate)]
          elif policyinfo[i][9]=='Half-yearly':
            date2=startdate+relativedelta(months=+6)
            startdate=startdate.strftime("%d-%m-%Y")
            date2=date2.strftime("%d-%m-%Y")
            lst = [('','1','2'),
           ('Cost',policyinfo[i][11]/2,policyinfo[i][11]/2),
           ('Date',startdate,date2)]
            
          elif policyinfo[i][9]=='Quaterly':
            date2=startdate+relativedelta(months=+3)
            date3=date2+relativedelta(months=+3)
            date4=date3+relativedelta(months=+3)
            
            startdate=startdate.strftime("%d-%m-%Y")
            date2=date2.strftime("%d-%m-%Y")
            date3=date3.strftime("%d-%m-%Y")
            date4=date4.strftime("%d-%m-%Y")
            lst = [('','1','2','3','4'),
          ('Cost',policyinfo[i][11]/4,policyinfo[i][11]/4,policyinfo[i][11]/4,policyinfo[i][11]/4),
          ('Date',startdate,date2,date3,date4)]
         
         #creating table
          for x in range(len(lst)):
            for y in range(len(lst[0])):
              installtable= Entry(viewdetails_frame, width=10, fg='black',
                               font=('Arial',12,'bold'))
                  
              installtable.grid(row=x+15, column=y)
              installtable.insert(END, lst[x][y])
        
          selfinslabel=Label( viewdetails_frame,text="Self damage insurance : ")
          selfinslabel.grid(row=18,column=0,pady=10)
          selfinsdata=Label(viewdetails_frame,text=policyinfo[i][12])
          selfinsdata.grid(row=18,column=1,pady=10)

          thirdinslabel=Label( viewdetails_frame,text="Third party damage insurance : ")
          thirdinslabel.grid(row=19,column=0,pady=10)
          thirdinsdata=Label(viewdetails_frame,text=policyinfo[i][13])
          thirdinsdata.grid(row=19,column=1,pady=10)

        button_profile=Button(second_frame,text="Profile",command=self.profile_win)
        button_profile.grid(row=0,column=2)
  
  #opens profile window
  def profile_win(self):
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Profile(self.root) 
      self.root.mainloop()
          
#--------------------Window to Buy Policy----------------------#
class Buy_Policy:
  def __init__(self,root):
        
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("Buy Policy")
        self.root.iconbitmap("icon.ico")

        self.var_age=StringVar()
        self.var_gender=StringVar()
        self.var_year=StringVar()
        self.var_city=StringVar()
        self.var_capacity=StringVar()
        self.var_price=StringVar()
        self.var_type=StringVar()
        self.var_installtype=StringVar()

        buypolicy_frame=LabelFrame(self.root,text="Buy Policy",padx=30,pady=30,bd=5)
        buypolicy_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        agelabel=Label(buypolicy_frame,text="Age")
        agelabel.grid(row=0,column=0,pady=10)
        self.ageentry=Entry(buypolicy_frame,width=35,borderwidth=5,textvariable=self.var_age)
        self.ageentry.grid(row=0,column=1)

        yearlabel=Label(buypolicy_frame,text="Year of registration")
        yearlabel.grid(row=1,column=0,pady=10)
        self.yearentry=Entry(buypolicy_frame,width=35,borderwidth=5,textvariable=self.var_year)
        self.yearentry.grid(row=1,column=1)
        
        caplabel=Label(buypolicy_frame,text="Cubic Capacity")
        caplabel.grid(row=2,column=0,pady=10)
        self.capentry=Entry(buypolicy_frame,width=35,borderwidth=5,textvariable=self.var_capacity)
        self.capentry.grid(row=2,column=1)

        pricelabel=Label(buypolicy_frame,text="Price")
        pricelabel.grid(row=3,column=0,pady=10)
        self.priceentry=Entry(buypolicy_frame,width=35,borderwidth=5,textvariable=self.var_price)
        self.priceentry.grid(row=3,column=1)

        genderlabel=Label(buypolicy_frame,text="Select Gender")
        genderlabel.grid(row=4,column=0)
        self.var_gender = StringVar(buypolicy_frame, "1")
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Male", variable = self.var_gender,value = "Male").grid(row=4,column=1)
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Female", variable = self.var_gender,value = "Female").grid(row=4,column=2)

        typelabel=Label(buypolicy_frame,text="Select Type Of Damage")
        typelabel.grid(row=5,column=0)
        self.var_type = StringVar(buypolicy_frame, "1")
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Self", variable = self.var_type,value = "Self").grid(row=5,column=1)
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Third Party", variable = self.var_type,value = "Third Party").grid(row=5,column=2)
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Both", variable = self.var_type,value = "Both").grid(row=5,column=3)
        
        citylabel=Label(buypolicy_frame,text="City")
        citylabel.grid(row=6,column=0)
        cityoptions = ['Select City','Mumbai','Pune','Nagpur','Aurangabad','Nashik']
        self.var_city = StringVar(buypolicy_frame, "Select City")
        self.dropmenu=OptionMenu( buypolicy_frame , self.var_city , *cityoptions ).grid(row=6,column=1)
       

        installtypelabel=Label(buypolicy_frame,text="Installment Type")
        installtypelabel.grid(row=7,column=0)
        self.var_installtype = StringVar(buypolicy_frame, "1")
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Yearly", variable = self.var_installtype,value = "Yearly").grid(row=7,column=1)
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Half-yearly", variable = self.var_installtype,value = "Half-yearly").grid(row=7,column=2)
        self.radiobutton=Radiobutton(buypolicy_frame, text = "Quaterly", variable = self.var_installtype,value = "Quaterly").grid(row=7,column=3)
        

        button_generate=Button(buypolicy_frame,text="Generate Policy",command=self.policy_conditions)
        button_generate.grid(row=8,column=1,pady=10)

        button_profile=Button(buypolicy_frame,text="Profile",command=self.profile_win)
        button_profile.grid(row=9,column=1,pady=10)
  
  #opens profile window
  def profile_win(self):
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Profile(self.root) 
      self.root.mainloop()

  #opens policy details window
  def details_win(self):
      global parent
      parent=self.root
      self.new_window=Toplevel(self.root)
      self.app=Policy_Details(self.new_window)

  #function to check policy_conditions
  def policy_conditions(self):
    global age,gender,capacity,price,city,year,damage,install
    flag=0
    if self.var_age.get()=="" or self.var_year.get()==""  or self.var_price.get()=="" or self.var_capacity.get()=="" or self.var_gender.get()=="1" or self.var_type.get()=="1" or self.var_installtype.get()=="1" or self.var_city.get()=="Select City" :
      messagebox.showerror("Error","All fields required")
      flag = 1
    elif self.var_age.get().isnumeric()==False or self.var_year.get().isnumeric==False or self.var_price.get().isnumeric()==False or self.var_capacity.get().isnumeric()==False:
        messagebox.showerror("Error","All fields should be integers. Round off to the nearest whole number")
        flag = 1
    else:
      mycursor.execute("SELECT MIN(min) AS minimum FROM agefactor")
      min_age = mycursor.fetchone()
      mycursor.execute("SELECT MAX(max) AS maximum FROM agefactor")
      max_age = mycursor.fetchone()
      mycursor.execute("SELECT MIN(min) AS minimum FROM pricefactor")
      min_price = mycursor.fetchone()
      mycursor.execute("SELECT MAX(max) AS maximum FROM pricefactor")
      max_price = mycursor.fetchone()
      mycursor.execute("SELECT MIN(min) AS minimum FROM yearfactor")
      min_year = mycursor.fetchone()
      mycursor.execute("SELECT MAX(max) AS maximum FROM yearfactor")
      max_year = mycursor.fetchone()
      mycursor.execute("SELECT MIN(min) AS minimum FROM capacityfactor")
      min_cc = mycursor.fetchone()
    
      mycursor.execute("SELECT MAX(max) AS maximum FROM capacityfactor")
      max_cc = mycursor.fetchone()
      if int(self.var_age.get())<min_age[0]:
        messagebox.showerror("Error","We do not provide insurance for people with age less than "+str(min_age[0]))
        flag= 1
      elif int(self.var_age.get())>max_age[0]:
        messagebox.showerror("Error","We do not provide insurance for people with age more than "+str(max_age[0]))
        flag= 1
      if int(self.var_price.get())<min_price[0]:
        messagebox.showerror("Error","We do not provide insurance for cars priced less than "+str(min_price[0]))
        flag= 1
      elif int(self.var_price.get())>max_price[0]:
        messagebox.showerror("Error","We do not provide insurance for cars priced more than "+str(max_price[0]))
        flag= 1
      digits = int(math.log10(int(self.var_year.get())))+1
      if digits!=4:
        messagebox.showerror("Error","Please enter year in YYYY format")
        flag= 1
      else:
        if int(self.var_year.get())<min_year[0]:
          messagebox.showerror("Error","We do not provide insurance for cars registered before "+str(min_year[0]))
          flag= 1
        elif int(self.var_year.get())>max_year[0]:
          messagebox.showerror("Error","Please enter correct year")
          flag= 1
      if int(self.var_capacity.get())<min_cc[0]:
        messagebox.showerror("Error","We do not provide insurance for car with capacity less than "+str(min_cc[0]))
        flag= 1
      elif int(self.var_capacity.get())>max_cc[0]:
        messagebox.showerror("Error","We do not provide insurance for car with capacity more than "+str(max_cc[0]))
        flag= 1
    
    if flag!=1:
        msgbox=messagebox.askquestion("Generate Policy","Do you want to generate the car insurance policy?")
        if msgbox=='yes':
            
            age=int(self.var_age.get())
            gender=self.var_gender.get()
            capacity=int(self.var_capacity.get())
            city=self.var_city.get()
            price=int(self.var_price.get())
            year=int(self.var_year.get())
            damage=self.var_type.get()
            install=self.var_installtype.get()
            self.details_win()

#-----------------------Window to view policy details--------------------------#    
class Policy_Details:
     def __init__(self,root):
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("Policy Details")
        self.root.iconbitmap("icon.ico")
        self.display_beforeconfirm()
        
     def display_beforeconfirm(self):

       query="Select * from userdata where %s=username"
       user=(username,)
       mycursor.execute(query,user)
       userinfo = mycursor.fetchone()
        

       policydetails_frame=LabelFrame(self.root,text="",padx=10,pady=30,bd=5)
       policydetails_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        #Personal details
       personallabel=Label( policydetails_frame,text="Personal Details")
       personallabel.grid(row=0,column=0,pady=10,columnspan=2)
       namelabel=Label( policydetails_frame,text="Name: ")
       namelabel.grid(row=1,column=0,pady=10)
       namedata=Label( policydetails_frame,text=userinfo[2])
       namedata.grid(row=1,column=1,pady=10)
       genderlabel=Label( policydetails_frame,text="Gender: ")
       genderlabel.grid(row=2,column=0,pady=10)
       genderdata=Label( policydetails_frame,text=gender)
       genderdata.grid(row=2,column=1,pady=10)
       agelabel=Label( policydetails_frame,text="Age: ")
       agelabel.grid(row=3,column=0,pady=10)
       agedata=Label( policydetails_frame,text=age)
       agedata.grid(row=3,column=1,pady=10)
      
        #Car details
       carlabel=Label( policydetails_frame,text="Car Details")
       carlabel.grid(row=4,column=0,pady=10,columnspan=2)
       yearlabel=Label( policydetails_frame,text="Year of registration: ")
       yearlabel.grid(row=5,column=0,pady=10)
       yeardata=Label( policydetails_frame,text=year)
       yeardata.grid(row=5,column=1,pady=10)
       citylabel=Label( policydetails_frame,text="City: ")
       citylabel.grid(row=6,column=0,pady=10)
       citydata=Label( policydetails_frame,text=city)
       citydata.grid(row=6,column=1,pady=10)
       pricelabel=Label( policydetails_frame,text="Price: ")
       pricelabel.grid(row=7,column=0,pady=10)
       pricedata=Label( policydetails_frame,text=price)
       pricedata.grid(row=7,column=1,pady=10)
       caplabel=Label( policydetails_frame,text="Capacity(in cc): ")
       caplabel.grid(row=8,column=0,pady=10)
       capdata=Label( policydetails_frame,text=capacity)
       capdata.grid(row=8,column=1,pady=10)

        #Insurance Details
       inslabel=Label( policydetails_frame,text="Insurance Details")
       inslabel.grid(row=9,column=0,pady=10,columnspan=2)
       damagelabel=Label( policydetails_frame,text="Type of damage: ")
       damagelabel.grid(row=10,column=0,pady=10)
       damagedata=Label( policydetails_frame,text=damage)
       damagedata.grid(row=10,column=1,pady=10)
       installlabel=Label( policydetails_frame,text="Premium installment type: ")
       installlabel.grid(row=11,column=0,pady=10)
       installdata=Label( policydetails_frame,text=install)
       installdata.grid(row=11,column=1,pady=10)

       global fac,premium,startdate,selfins,thirdins
       fac=self.factorcalc()
       if damage=='Self':
         premium=price*fac*0.8
       elif damage=='Both':
         premium=price*fac*1.3
       else:
         premium=price*fac
       premiumlabel=Label( policydetails_frame,text="Premium : ")
       premiumlabel.grid(row=12,column=0,pady=10)
       premiumdata=Label( policydetails_frame,text=premium)
       premiumdata.grid(row=12,column=1,pady=10)
       
       startdate=date.today()+ timedelta(days=7)
       if install=='Yearly':
         startdate=startdate.strftime("%d-%m-%Y")
         lst = [('','1'),
           ('Cost',premium),
           ('Date',startdate)]
       if install=='Half-yearly':
         date2=startdate+relativedelta(months=+6)
         startdate=startdate.strftime("%d-%m-%Y")
         date2=date2.strftime("%d-%m-%Y")
         lst = [('','1','2'),
           ('Cost',premium/2,premium/2),
           ('Date',startdate,date2)]
            
       if install=='Quaterly':
         date2=startdate+relativedelta(months=+3)
         date3=date2+relativedelta(months=+3)
         date4=date3+relativedelta(months=+3)
            
         startdate=startdate.strftime("%d-%m-%Y")
         date2=date2.strftime("%d-%m-%Y")
         date3=date3.strftime("%d-%m-%Y")
         date4=date4.strftime("%d-%m-%Y")
         lst = [('','1','2','3','4'),
          ('Cost',premium/4,premium/4,premium/4,premium/4),
          ('Date',startdate,date2,date3,date4)]
         
       for i in range(len(lst)):
         for j in range(len(lst[0])):
           installtable= Entry(policydetails_frame, width=10, fg='black',
                               font=('Arial',12,'bold'))
                  
           installtable.grid(row=i+13, column=j)
           installtable.insert(END, lst[i][j])

       if damage=='Self':
         selfins=price*0.2
         thirdins=0
       elif damage=='Both':
         selfins=price*0.2
         thirdins=price*0.3
       else:
         selfins=0
         thirdins=price*0.3
       
       selfinslabel=Label( policydetails_frame,text="Self damage insurance : ")
       selfinslabel.grid(row=16,column=0,pady=10)
       selfinsdata=Label(policydetails_frame,text=selfins)
       selfinsdata.grid(row=16,column=1,pady=10)

       thirdinslabel=Label( policydetails_frame,text="Third party damage insurance : ")
       thirdinslabel.grid(row=17,column=0,pady=10)
       thirdinsdata=Label(policydetails_frame,text=thirdins)
       thirdinsdata.grid(row=17,column=1,pady=10)

       button_generate=Button(policydetails_frame,text="Go Back",command=self.back_generate_win)
       button_generate.grid(row=18,column=0,pady=10)

       button_buypolicy=Button(policydetails_frame,text="Buy policy",command=self.before_confirm)
       button_buypolicy.grid(row=18,column=1,pady=10)

     #destroys current window and goes to previous window  
     def back_generate_win(self):
          self.root.destroy() # close the current window
          parent.deiconify()

     def factorcalc(self):
       factor=0
       global age,gender,capacity,price,city,year,damage,install
       
       query="Select factor from genderfactor where %s=gender"
       genvar=(gender,)
       mycursor.execute(query,genvar)
       myresult = mycursor.fetchone()
       factor=factor+myresult[0]
       
       query="Select factor from cityfactor where %s=city"
       cityvar=(city,)
       mycursor.execute(query,cityvar)
       myresult = mycursor.fetchone()
       factor=factor+myresult[0]
    
       query="Select factor from agefactor where %s>=min and %s<=max"
       agevar=(age,age)
       mycursor.execute(query, agevar)
       myresult = mycursor.fetchone()
       factor=factor+myresult[0]
      
       query="Select factor from pricefactor where %s>=min and %s<=max"
       pricevar=(price,price)
       mycursor.execute(query, pricevar)
       myresult = mycursor.fetchone()
       factor=factor+myresult[0]

       query="Select factor from yearfactor where %s>=min and %s<=max"
       yearvar=(year,year)
       mycursor.execute(query, yearvar)
       myresult = mycursor.fetchone()
       factor=factor+myresult[0]
       
       query="Select factor from capacityfactor where %s>=min and %s<=max"
       capvar=(capacity,capacity)
       mycursor.execute(query, capvar)
       myresult = mycursor.fetchone()
       factor=factor+myresult[0]
       return factor
     
     #opens window after user confirms
     def after_confirm(self):
       
       self.root.destroy() # close the current window
       self.root = Tk() # create another Tk instance
       self.app = Confirm_Window(self.root) 
       self.root.mainloop()

     def before_confirm(self):  
        parent.withdraw()
        global p_id,startdate
        
        msgbox=messagebox.askquestion("Confirm policy","Do you want to purchase the car insurance policy?")
        if msgbox=='yes':
          p_id=str(uuid.uuid4().fields[-1])[:7]
          today=date.today()
          mycursor.execute("insert into policy values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(username,
                                                                             p_id,gender,age,year,city,capacity,
                                                                             price,today,install,damage,premium,
                                                                             selfins,thirdins
                                                                            ))
          mydb.commit()
          self.after_confirm()
          
#---------------Confirmation window----------------------------#
class Confirm_Window():
  def __init__(self,root):
        
        self.root=root
        self.root.geometry("1000x1000+130+0")  
        self.root.title("Confirmation Window")
        self.root.iconbitmap("icon.ico")
        
        query =("SELECT * FROM policy WHERE policy_id = %s")
        value=(p_id,)
        mycursor.execute(query,value)
        policyinfo=mycursor.fetchone()
        confirmdetails_frame=LabelFrame(self.root,text="",padx=10,pady=30,bd=5)
        confirmdetails_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        policyidlabel=Label(confirmdetails_frame,text="Policy ID: ")
        policyidlabel.grid(row=0,column=0,pady=10)
        policyiddata=Label( confirmdetails_frame,text=policyinfo[1])
        policyiddata.grid(row=0,column=1,pady=10)
        premiumlabel=Label(confirmdetails_frame,text="Premium: ")
        premiumlabel.grid(row=1,column=0,pady=10)
        premiumdata=Label( confirmdetails_frame,text=policyinfo[11])
        premiumdata.grid(row=1,column=1,pady=10)
        insuredlabel=Label(confirmdetails_frame,text="Insured Amount: ")
        insuredlabel.grid(row=2,column=0,pady=10)
        selfinslabel=Label(confirmdetails_frame,text="Self Damage: ")
        selfinslabel.grid(row=3,column=0,pady=10)
        selfinsdata=Label( confirmdetails_frame,text=policyinfo[12])
        selfinsdata.grid(row=3,column=1,pady=10)
        thirdinslabel=Label(confirmdetails_frame,text="Third-Party Damage: ")
        thirdinslabel.grid(row=4,column=0,pady=10)
        thirdinsdata=Label( confirmdetails_frame,text=policyinfo[13])
        thirdinsdata.grid(row=4,column=1,pady=10)

        button_download=Button(confirmdetails_frame,text="Download Policy",command=self.download)
        button_download.grid(row=5,column=1,pady=10)

        button_profile=Button(confirmdetails_frame,text="Profile",command=self.profile_win)
        button_profile.grid(row=6,column=1,pady=10)

  def profile_win(self):
      self.root.destroy() # close the current window
      self.root = Tk() # create another Tk instance
      self.app = Profile(self.root) 
      self.root.mainloop()

  #creates pdf  
  def download(self):
    global p_id
    query =("SELECT * FROM userdata WHERE username = %s")
    value=(username,)
    mycursor.execute(query,value)
    userinfo=mycursor.fetchone()
    query =("SELECT * FROM policy WHERE policy_id = %s")
    value=(p_id,)
    mycursor.execute(query,value)
    policyinfo=mycursor.fetchone()
    pdf = FPDF()
    pdf.add_page()
    epw = pdf.w - 2*pdf.l_margin
    pdf.set_font("Times", size = 20)
    pdf.line(10, 30, 200, 30)
    
    pdf.cell(epw, 20, txt = "Car Insurance Policy",
         ln = 1, align = 'C')
    
    col_width = epw/2
    data = [['Name: '+userinfo[2],'Email ID: '+userinfo[3]],
['Gender:'+policyinfo[2],'Age: '+str(policyinfo[3])]
]
    th = pdf.font_size 
    pdf.set_font('Times','B',14.0) 
    pdf.ln(th)
    pdf.cell(epw, 0.0, 'Personal Details', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(th)
    
    for row in data:
        for datum in row:
            
            pdf.cell(col_width, th, str(datum), border=1,align='L')
    
        pdf.ln(th)
    
    pdf.ln(th)
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, 0.0, 'Car Details', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(th)
    
    col_width_veh = epw/3
   
    data = [
['Year Of Registration:'+str(policyinfo[4]),'City: '+policyinfo[5],'Vehicle CC: '+str(policyinfo[6])]
]
    for row in data:
        for datum in row:
            
            pdf.cell(col_width_veh, th, str(datum), border=1,align='L')
    
        pdf.ln(th)
    
    pdf.ln(th)
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, 0.0, 'Policy Details', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(th)
    
    startdate=policyinfo[8]+ timedelta(days=7) 
    expdate=startdate+relativedelta(years=+1)-timedelta(days=1)
    startdate=startdate.strftime("%d-%m-%Y") 
    expdate=expdate.strftime("%d-%m-%Y")
    
    data = [['Policy ID: '+str(policyinfo[1]),'Premium Amount: '+str(policyinfo[11])],
        ['Self Damage insurance: '+str(policyinfo[12]),'Third Party Damage insurance: '+str(policyinfo[13])],
        ['Policy Active Date: '+str(startdate),'Policy Expiration Date: '+str(expdate)]
       ]
    for row in data:
        for datum in row:
            
            pdf.cell(col_width, th, str(datum), border=1,align='L')
    
        pdf.ln(th)
    
    pdf.ln(th)
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, 0.0, 'Installment Schedule', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(th)
    
    
    startdate=policyinfo[8]+ timedelta(days=7)    
    if policyinfo[9]=='Yearly':
        startdate=startdate.strftime("%d-%m-%Y")
        data_date = [['Payment Date: ','Cost: '],[str(startdate),str(policyinfo[11])]]
    
    elif policyinfo[9]=='Half-yearly':
        date2=startdate+relativedelta(months=+6)
        startdate=startdate.strftime("%d-%m-%Y")
        date2=date2.strftime("%d-%m-%Y")
        
        data_date = [['Payment Date: ','Cost: '],
        [str(startdate),str(policyinfo[11]/2)],
        [str(date2),str(policyinfo[11]/2)]
        ]
    
    elif policyinfo[9]=='Quaterly':
        date2=startdate+relativedelta(months=+3)
        date3=date2+relativedelta(months=+3)
        date4=date3+relativedelta(months=+3)   
        startdate=startdate.strftime("%d-%m-%Y")
        date2=date2.strftime("%d-%m-%Y")
        date3=date3.strftime("%d-%m-%Y")
        date4=date4.strftime("%d-%m-%Y")
        data_date = [['Payment Date: ','Cost: '],
        [str(startdate),str(policyinfo[11]/4)],
        [str(date2),str(policyinfo[11]/4)],
        [str(date3),str(policyinfo[11]/4)],
        [str(date4),str(policyinfo[11]/4)]
        ]
    
    for row in data_date:
        for datum in row:
            
            pdf.cell(col_width, th, str(datum), border=1,align='L')
    
        pdf.ln(th)
    
    filename=str(p_id)+".pdf"
    pdf.output(filename)  
    messagebox.showinfo("Download Complete","Policy has been downloaded")


if __name__=="__main__":
    main()



