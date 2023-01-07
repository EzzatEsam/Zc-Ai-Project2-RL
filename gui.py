from doctest import master
import tkinter as tk;
from PIL import Image, ImageTk
import customtkinter as ct;


MAP_NAME = 'map.png'
class gui_handler :
    def __init__(self) -> None:
        ct.set_appearance_mode("system")  # Modes: system (default), light, dark
        ct.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        root = ct.CTk();
        root.geometry("800x400")
        button = ct.CTkButton(master=root, text="CTkButton")
        button.place(x = 400 , y = 20)

        combobox = ct.CTkOptionMenu(master=root,
                                       values=["option 1", "option 2"],
                                       )
        combobox.place(x = 400 , y = 200)
        combobox.set("option 2")  # set initial value

        window =ct.CTkCanvas( master = root ,width= 400, height=400)
        window.place(x =0 ,y= 0)

        img = Image.open(MAP_NAME)
        self.map_img = ImageTk.PhotoImage(img)
        self.zc_map = window.create_image(0,0 ,image = self.map_img , anchor="nw")

        root.mainloop()

        pass