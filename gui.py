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
    
    def draw_next_state(self , t= 0.3e3 ) :
        state = self.states[self.idx]
        env = self.env
        self.idx +=1
        pos ,currently_holding ,  pickup_locations = env.decode_state(state)
        self.robot_loc = pos 
        self.crate_locs = [ building_to_position[bl] for bl in pickup_locations if bl > 0]

        if currently_holding :
            self.target_loc  = building_to_position[ env.dropoff_locations[currently_holding -1] ]  

        self.draw_objects()
        self.root.after(int(t) , func=self.draw_next_state)



    def get_states(self) :
        self.ai.start()
        self.idx = 0
        self.states = self.ai.states
        self.env = self.ai.env
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

    def draw_objects(self ) :
        self.reset();
        
        self.robot = self.window.create_image( self.robot_loc[0] * BOX_DIM ,self.robot_loc[1] * BOX_DIM  , anchor='nw', image= self.robot_img )
        if self.target_loc : 
            self.loc = self.window.create_image( self.target_loc[0] * BOX_DIM ,self.target_loc[1] * BOX_DIM  , anchor='nw', image= self.target_img )

        if self.crate_locs :
            self.crates = [ 
                self.window.create_image( cloc[0] * BOX_DIM ,cloc[1] * BOX_DIM  , anchor='nw', image= self.crate_img ) 
                for cloc in self.crate_locs
            ]
        

        


    def start_ui(self) :
        ct.set_appearance_mode("system")  # Modes: system (default), light, dark
        ct.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        root = ct.CTk();
        root.geometry("800x600")
        button = ct.CTkButton(master=root,  text="Start" , command= self.get_states)
        button.place(x = 600 , y = 20)

        combobox = ct.CTkOptionMenu(master=root,
                                       values=["option 1", "option 2"],
                                       )
        combobox.place(x = 600 , y = 200)
        combobox.set("option 2")  # set initial value

        window =ct.CTkCanvas( master = root ,width= 520, height=520)
        window.place(x =0 ,y= 0)

        img = Image.open(MAP_NAME).resize((PHOTO_DIM,PHOTO_DIM), Image.ANTIALIAS)
        self.map_img = ImageTk.PhotoImage(img )
        self.zc_map = window.create_image(0,0 ,image = self.map_img , anchor="nw")

        
        self.robot_img = ImageTk.PhotoImage(Image.open(ROBOT_PATH).resize((BOX_DIM,BOX_DIM), Image.ANTIALIAS)  )
        self.crate_img = ImageTk.PhotoImage(Image.open(CRATE_PATH).resize((BOX_DIM,BOX_DIM), Image.ANTIALIAS)  )
        self.target_img = ImageTk.PhotoImage(Image.open(TARGEt_PATH).resize((BOX_DIM,BOX_DIM), Image.ANTIALIAS)  )
        

        self.root = root ; 
        self.window = window
        root.mainloop()

    def __init__(self , ai_master_cls) -> None:
        self.ai = ai_master_cls
        self.target_loc = (1 ,2);
        self.crate_locs = [ (4 ,5) ,(6,7)];
        self.robot_loc =  (12 ,5)
        self.robot = None ;
        self.crates = None ;
        self.loc = None ;
        self.start_ui()

