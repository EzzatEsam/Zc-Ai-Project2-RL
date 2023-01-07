
from time import sleep
import flet as ft

class gui_ft_handler :
    def start(self, page : ft.page) :
        t = ft.Text(value="Hello, world!", color="green")
        first_name = ft.TextField()
        page.add(t , first_name)
        page.update()
        while 1 : x =2

    def __init__(self) -> None:
        ft.app(target= self.start , view= 'flet_app')
        print('test')
        pass

gui_ft_handler()
