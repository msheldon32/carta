import tkinter as tk
import carta
import carta_local
import interaction
import carta_review_schemes

class DataSourceMenuWindow(tk.Frame):
	def __init__(self, menu_obj, master=None):
		super().__init__(master)
		
		self.menu_obj = menu_obj
		self.refresh_vars()
		
		self.pack()
		self.create_widgets()
	
	def refresh_vars(self):
		self.data_frame_names = tk.StringVar(value=[dset.name() for dset in self.session.data_sets])
	
	def create_widgets(self):
		self.source_list = tk.Listbox(self, height=10, listvariable=self.data_frame_names)
		
		self.add_button = tk.Button(self)
		self.add_button["text"] = "Add"
		
		self.edit_button = tk.Button(self)
		self.edit_button["text"] = "Edit"
		
		self.delete_button = tk.Button(self)
		self.delete_button["text"] = "Delete"
		
		self.source_list.grid(row=0, column=0, rowspan=3)
		self.add_button.grid(row=0, column=1)
		self.edit_button.grid(row=1, column=1)
		self.delete_button.grid(row=2, column=1)
		
class CartaMainMenuWindow(tk.Frame):
	def __init__(self, menu_obj, master=None):
		super().__init__(master)
		
		self.menu_obj = menu_obj
		
		self.pack()
		self.create_widgets()
		
	def create_widgets(self):
                self.data_set_button = tk.Button(self)
                self.data_set_button["text"] = "Data Sets"
                self.data_set_button["command"] = (lambda: DataSourceMenu(self.session, self.master))
                
                self.deck_button = tk.Button(self)
                self.deck_button["text"] = "Decks"
                
                self.data_set_button.grid(row=0, column=0)
                self.deck_button.grid(row=0, column=1)

if __name__=="__main__":
        data_state = interaction.DataState("carta_data.p")
        main_menu = interaction.MainMenu(data_state)
        root = tk.Tk()
        main_menu_window = CartaMainMenuWindow(main_menu, master=root)
        main_menu_window.mainloop()
