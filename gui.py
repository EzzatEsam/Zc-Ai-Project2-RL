from cgitb import text
from doctest import master
import tkinter as tk;
from PIL import Image, ImageTk
import customtkinter as ct;
from map_data import *
from Solvers import *


MAP_NAME = 'map.png'
ROBOT_PATH = 'icons/robot.png'
CRATE_PATH = 'icons/wooden-box.png'
TARGEt_PATH = 'icons/location.png'
PHOTO_DIM = 504
BOX_DIM = int(PHOTO_DIM/14) 

class gui_handler :
    
    def draw_next_state(self  ) :
        if (self.stopped) :
            self.states = []
            self.reset()
            return
        
        t = float(self.t.get())  * 1e3
        state = self.states[self.idx]
        env = self.env
        self.idx +=1
        if self.idx == len(self.states) :
            return

        pos ,currently_holding ,  pickup_locations = env.decode_state(state)
        self.robot_loc = pos 
        self.crate_locs = [ building_to_position[bl] for bl in pickup_locations if bl > 0]

        self.nb_boxes.configure(text =  f'NB boxes : {sum(loc == 3 for loc in pickup_locations )}')
        self.hb_boxes.configure(text =  f'HB boxes : {sum(loc == 4 for loc in pickup_locations)}')

        if currently_holding :
            self.target_loc  = building_to_position[ env.dropoff_locations[currently_holding -1] ] 
        else :
            self.target_loc = None 

        self.draw_objects()
        self.root.after(int(t) , func=self.draw_next_state)


    def begin_train(self) :
        self.ai.train(  alg = self.alg.get(), iterations = int(self.iterations.get())  ,save_table = self.save2table.get() ,
        learning_rate = self.alpha.get() , discount = float(self.discount.get()) 
        )

    def stop_sim(self) :
        self.stopped = True;


    def get_states(self) :
        self.stopped = False;
        self.ai.start()
        self.idx = 0
        self.states = self.ai.states
        self.env = self.ai.env
        self.path_len.configure(text =f'Path length : {len(self.states)}' )
        self.draw_next_state()
        
        

    def reset(self) :
        if self.loc : 
            self.window.delete(self.loc);
            self.loc = None 
        if self.robot : 
            self.window.delete(self.robot);
            self.loc = None 
        if self.crates : 
            for crate in self.crates :
                self.window.delete(crate);
            self.crates = [] 
        # self.nb_boxes.configure(text =  'NB boxes :')
        # self.hb_boxes.configure(text =  'HB boxes :')

    def draw_objects(self ) :
        self.reset();
        
        if self.target_loc : 
            self.loc = self.window.create_image( self.target_loc[0] * BOX_DIM ,self.target_loc[1] * BOX_DIM  , anchor='nw', image= self.target_img )

        if self.crate_locs :
            self.crates = [ 
                self.window.create_image( cloc[0] * BOX_DIM ,cloc[1] * BOX_DIM  , anchor='nw', image= self.crate_img ) 
                for cloc in self.crate_locs
            ]
        
        self.robot = self.window.create_image( self.robot_loc[0] * BOX_DIM ,self.robot_loc[1] * BOX_DIM  , anchor='nw', image= self.robot_img )

        


    def start_ui(self) :
        ct.set_appearance_mode("system")  # Modes: system (default), light, dark
        ct.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        root = ct.CTk();
        root.geometry("800x510")
        root.resizable(False, False)
        root.title('ZC pathfinder')
        


        label1 = ct.CTkLabel(master= root ,text= 'Iterations')
        label1.place(x = 600 , y = 5)

        self.iterations = ct.StringVar(root)
        combobox = ct.CTkOptionMenu(master=root, variable= self.iterations ,
                                       values=["5", "10" ,"100" , "200" ,'300'  ,'400', "500" , "1000" ,'2000' , "3000"],
                                       )
        combobox.place(x = 550 , y = 30)
        combobox.set("200")  # set initial value


        self.alg = ct.StringVar(root)
        combobox2 = ct.CTkOptionMenu(master=root, variable= self.alg ,
                                       values=["greedy", "random" ,"exploring" ],
                                       )
        combobox2.place(x = 550 , y = 90)
        combobox2.set("exploring")  # set initial value

        label2 = ct.CTkLabel(master= root ,text= 'Algorithm')
        label2.place(x = 600 , y = 90-30)

        self.t = ct.StringVar(root)
        combobox3 = ct.CTkOptionMenu(master=root, variable= self.t ,
                                       values=['0.01','0.05' ,"0.1", "0.2" ,"0.3" , "0.5" ], width= 40
                                       )
        combobox3.place(x = 700 , y = 250)
        combobox3.set("0.2")  # set initial value

        label3 = ct.CTkLabel(master= root ,text= 'simulation time')
        label3.place(x = 700 , y = 250-30)


        self.discount = ct.StringVar(root)
        combobox4 = ct.CTkOptionMenu(master=root, variable= self.discount ,
                                       values=['0.1','0.2' ,"0.3", "0.4" ], width= 40
                                       )
        combobox4.place(x = 700 , y = 30)
        combobox4.set("0.3")  # set initial value

        label4 = ct.CTkLabel(master= root ,text= 'Discount')
        label4.place(x = 700 , y = 5)
#############
        self.alpha = ct.StringVar(root)
        combobox5 = ct.CTkOptionMenu(master=root, variable= self.alpha ,
                                       values=["Normal" , '0.1' ,'0.3'  , '0.5' , '0.7' ], width= 40
                                       )
        combobox5.place(x = 700 , y = 90)
        combobox5.set("Normal")  # set initial value

        label5 = ct.CTkLabel(master= root ,text= 'Learning rate')
        label5.place(x = 700 , y = 90-30)

        button1 = ct.CTkButton(master=root,  text="Train" , command= self.begin_train)
        button1.place(x = 550 , y = 150)

        self.save2table = ct.BooleanVar(master= root);
        chkbox1 = ct.CTkCheckBox(master = root ,text= 'Save table' ,variable= self.save2table)
        chkbox1.place(x = 700 , y = 150)

        button = ct.CTkButton(master=root,fg_color = 'green' , text="Start" , command= self.get_states )
        button.place(x = 550 , y = 250)

        button3 = ct.CTkButton(master=root,fg_color = 'red' , text="Stop Simulation" , command= self.stop_sim )
        button3.place(x = 550 , y = 300)

        window =ct.CTkCanvas( master = root ,width= 504, height=510)
        window.place(x =0 ,y= 0)

        img = Image.open(MAP_NAME).resize((PHOTO_DIM,PHOTO_DIM), Image.ANTIALIAS)
        self.map_img = ImageTk.PhotoImage(img )
        self.zc_map = window.create_image(0,0 ,image = self.map_img , anchor="nw")

        
        self.robot_img = ImageTk.PhotoImage(Image.open(ROBOT_PATH).resize((BOX_DIM,BOX_DIM), Image.ANTIALIAS)  )
        self.crate_img = ImageTk.PhotoImage(Image.open(CRATE_PATH).resize((BOX_DIM,BOX_DIM), Image.ANTIALIAS)  )
        self.target_img = ImageTk.PhotoImage(Image.open(TARGEt_PATH).resize((BOX_DIM,BOX_DIM), Image.ANTIALIAS)  )

        #
        self.nb_boxes = ct.CTkLabel(master= root , text= 'NB boxes :') ;
        self.nb_boxes.place(x = 550 , y = 350) ;

        self.hb_boxes = ct.CTkLabel(master= root , text= 'HB boxes :') ;
        self.hb_boxes.place(x = 550 , y = 380) ;

        self.path_len = ct.CTkLabel(master= root , text= 'Path length :') ;
        self.path_len.place(x = 550 , y = 400) ;


        

        self.root = root ; 
        self.window = window
        root.mainloop()

    def __init__(self , ai_master_cls) -> None:
        self.ai = ai_master_cls
        self.target_loc = None;
        self.crate_locs = None
        self.robot_loc =  None
        self.robot = None ;
        self.crates = None ;
        self.loc = None ;
        self.start_ui()

