import customtkinter as cstk
import tkinter as tk

info_text = 'Cell counts: {num}\nstep: {step}'
local_minimum_cell = 2 # >=
local_maximum_cell = 3 # <=
generate_minimum_cell = 3 # >=
generate_maximum_cell = 3 # <=
near_range = 1
step_time = 500 # ms

class StringVar(cstk.StringVar):
    def get(self) -> int:
        try:
            return int(super().get()) if int(super().get()) > 0 else 1
        except ValueError:
            return 1
        
class World(tk.Canvas):
    def __init__(self, master: 'App', world_size: tuple[int, int]):
        super().__init__(master, background='#ffffff', width=min(world_size), height=min(world_size))
        self.world = master
        self.bind('<Button-1>', self.click)
        self.cell_alive_map: list[list[bool]] = []

        for i in range(world_size[0]):
            self.cell_alive_map.append([])
            for j in range(world_size[1]):
                self.cell_alive_map[i].append(False)

    def cell_numbers(self, map=None):
        tmp = []
        if map is None:
            map = self.cell_alive_map
        for i in map:
            tmp += i
        return sum(tmp)

    def click(self, event):
        x, y = self.get_cell_coord(event.x, event.y)
        self.cell_alive_map[y][x] = not self.cell_alive_map[y][x]
        self.create_cell((x, y))

    def create_cell(self, coord: tuple[int, int], scale: float = 0, *, map=None):
        x, y = coord
        tmp_x = self.winfo_width() / int(self.world.world_size[0].get())
        tmp_y = self.winfo_height() / int(self.world.world_size[1].get())

        scale = scale if scale > 0 else 0
        if map is None:
            map = self.cell_alive_map

        self.create_rectangle(tmp_x * x + max(tmp_x * scale, 2 if scale else 1),
                              tmp_y * y + max(tmp_y * scale, 2 if scale else 1),
                              tmp_x * (x+1) - max(tmp_x * scale, 1 if scale else 0),
                              tmp_y * (y+1) - max(tmp_y * scale, 1 if scale else 0),
                              width=0,
                              fill='#888888' if map[y][x] else '#ffffff')
        self.world.info_label.configure(text=info_text.format(num=self.cell_numbers(map), step=self.world.simulation_step))

    def get_cell_coord(self, canvas_x: int, canvas_y: int):
        tmp_x = self.winfo_width() / int(self.world.world_size[0].get())
        tmp_y = self.winfo_height() / int(self.world.world_size[1].get())

        return int(canvas_x // tmp_x), int(canvas_y // tmp_y)

    def render(self):
        self.master.update()
        tmp = self.winfo_width() / int(self.world.world_size[0].get())
        for i in range(int(self.world.world_size[0].get())):
            self.create_line(tmp * i, 0, tmp * i, self.winfo_height(), fill='#000000')

        tmp = self.winfo_height() / int(self.world.world_size[1].get())
        for i in range(int(self.world.world_size[1].get())):
            self.create_line(0, tmp * i, self.winfo_width(), tmp * i, fill='#000000')

class App(cstk.CTk):
    def __init__(self, window_size: tuple[int, int], world_size: tuple[int, int], fg_color=None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.simulation_id = None
        self.simulation_step = 0

        self.world_size: tuple[StringVar, StringVar] = (StringVar(self, str(world_size[0]), 'world_size_x'), StringVar(self, str(world_size[1]), 'world_size_y'))
        self.geometry(f'{window_size[0]}x{window_size[1]}+100+0')
        self.resizable(False, False)
        self.title('Life of game')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.world_map = World(self, world_size)
        self.world_map.grid(column=0, row=0, sticky='nswe', padx=5, pady=5, rowspan=4)

        self.info_label = cstk.CTkLabel(self, text=info_text.format(num=0, step=0))
        self.info_label.grid(column=1, row=0, sticky='nswe', padx=5, pady=5)

        self.world_size_x_entry = cstk.CTkEntry(self, placeholder_text=f'{self.world_size[0].get()}', textvariable=self.world_size[0])
        self.world_size_y_entry = cstk.CTkEntry(self, placeholder_text=f'{self.world_size[1].get()}', textvariable=self.world_size[1])
        self.world_size_x_entry.grid(column=1, row=1, sticky='we', padx=5, pady=5)
        self.world_size_y_entry.grid(column=1, row=2, sticky='we', padx=5, pady=5)
        self.world_size_x_entry.bind('<Return>', self.slider_x)
        self.world_size_y_entry.bind('<Return>', self.slider_y)

        self.start_button = cstk.CTkButton(self, text='Start!', command=self.execute, fg_color='#6666ff')
        self.start_button.grid(column=1, row=3, sticky='wes', padx=5, pady=5)

        self.world_map.render()

    def refresh_render(self):
        self.world_map.create_rectangle(0, 0, self.world_map.winfo_width(), self.winfo_height(), width=0,
                                        fill='#ffffff')
        self.world_map.render()
        for i in range(self.world_size[1].get()):
            for j in range(self.world_size[0].get()):
                self.world_map.create_cell((j, i))

    def slider_x(self, _):
        value = self.world_size[0].get()
        original_len = len(self.world_map.cell_alive_map[0])

        if original_len > value:
            for i in range(self.world_size[1].get()):
                del self.world_map.cell_alive_map[i][value:]
        elif original_len < value:
            for i in range(self.world_size[1].get()):
                for _ in range(value - original_len):
                    self.world_map.cell_alive_map[i].append(False)

        self.refresh_render()

    def slider_y(self, _):
        value = self.world_size[1].get()
        original_len = len(self.world_map.cell_alive_map[1])

        if original_len > value:
            del self.world_map.cell_alive_map[value:]
        elif original_len < value:
            for i in range(value - original_len):
                self.world_map.cell_alive_map.append([])
                for j in range(self.world_size[0].get()):
                    self.world_map.cell_alive_map[-1].append(False)

        self.refresh_render()

    def reset_state(self):
        self.simulation_id = None
        self.simulation_step = 0
        self.start_button.configure(text='Start!', fg_color='#6666ff')
        self.world_size_x_entry.configure(state=cstk.NORMAL)
        self.world_size_y_entry.configure(state=cstk.NORMAL)

    def execute(self):
        if self.simulation_id is None:
            self.simulation_id = self.after(step_time, self.run_generation)
            self.start_button.configure(text='Stop!', fg_color='#562482')
            self.world_size_x_entry.configure(state=cstk.DISABLED)
            self.world_size_y_entry.configure(state=cstk.DISABLED)
        else:
            self.after_cancel(self.simulation_id)
            self.reset_state()

    def run_generation(self):
        if self.simulation_id is None:
            return

        self.simulation_step += 1
        tmp_map = []
        for i in range(self.world_size[0].get()):
            tmp_map.append([])
            for j in range(self.world_size[1].get()):
                near_living = 0

                for i_i in range(i - near_range, i + 1 + near_range):
                    for j_j in range(j - near_range, j + 1 + near_range):
                        if i_i == i and j_j == j:
                            continue
                        if self.world_map.cell_alive_map[i_i % self.world_size[1].get()][j_j % self.world_size[0].get()]:
                            near_living += 1

                if local_minimum_cell <= near_living <= local_maximum_cell and self.world_map.cell_alive_map[i][j]:
                    tmp_map[i].append(True)
                elif not self.world_map.cell_alive_map[i][j] and generate_minimum_cell <= near_living <= generate_maximum_cell:
                    tmp_map[i].append(True)
                else:
                    tmp_map[i].append(False)

                self.world_map.create_cell((j, i), map=tmp_map)

        self.world_map.cell_alive_map = tmp_map

        if self.world_map.cell_numbers() != 0:
            self.simulation_id = self.after(step_time, self.run_generation)
        else:
            self.reset_state()


world = App((700, 600), (10, 10))
world.mainloop()