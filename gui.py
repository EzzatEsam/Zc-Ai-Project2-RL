from doctest import master
import tkinter as tk;
from PIL import Image, ImageTk
import customtkinter as ct;


MAP_NAME = 'map.png'
ROBOT_PATH = 'icons/robot.png'
CRATE_PATH = 'icons/wooden-box.png'
TARGEt_PATH = 'icons/location.png'
PHOTO_DIM = 504
BOX_DIM = int(PHOTO_DIM/14) 

class gui_handler :

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
        button = ct.CTkButton(master=root,  text="CTkButton")
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
        self.draw_objects()
        root.mainloop()

    def __init__(self) -> None:
        self.target_loc = (1 ,2);
        self.crate_locs = [ (4 ,5) ,(6,7)];
        self.robot_loc =  (12 ,5)
        self.robot = None ;
        self.crates = None ;
        self.loc = None ;
        self.start_ui()
        