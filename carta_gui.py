import tkinter as tk
import carta
import carta_local

class CartaSession:
	def __init__(self):
		carta_data = carta.load_from_file("carta_data.json")
		self.data_sets = carta_data["data_sets"]
		self.decks = carta_data["decks"]
		self.reviews = carta_data["reviews"]

class DataSourceMenu(tk.Frame):
	def __init__(self, session, master=None):
		super().__init__(master)
		
		self.session = session
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
		
class CartaMainMenu(tk.Frame):
	def __init__(self, session, master=None):
		super().__init__(master)
		
		self.session = session
		
		self.pack()
		self.create_widgets()
		
	def create_widgets(self):
		self.data_set_button = tk.Button(self)
		self.data_set_button["text"] = "Data Sets"
		self.data_set_button["command"] = (lambda: DataSourceMenu(self.session, self.master))
		
		self.deck_button = tk.Button(self)
		self.deck_button["text"] = "Decks"
		
		self.review_button = tk.Button(self)
		self.review_button["text"] = "Review"
		
		self.data_set_button.grid(row=0, column=0)
		self.deck_button.grid(row=0, column=1)
		self.review_button.grid(row=1, column=0)

if __name__=="__main__":
	root = tk.Tk()
	main_menu = CartaMainMenu(CartaSession(), master=root)
	main_menu.mainloop()
