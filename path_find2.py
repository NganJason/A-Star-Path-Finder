import pygame 
import math


pygame.init()
screen_width = 800
screen_height = 800
n = 50
box_size = screen_width//n
running = True
screen = pygame.display.set_mode((screen_width, screen_height))

#Color code
white  = (255, 255, 255)
green = (0, 255, 0)
purple = (128, 0, 128)
red = (255, 0, 0)
black = (0, 0, 0)
orange = (255, 165 ,0)
turquoise = (64, 224, 208)
grey = (128, 128, 128)
color_dict = {
    "idle": white, 
    "start": orange, 
    "end": turquoise, 
    "barrier": black, 
    "close": red, 
    "open": green, 
    "path": purple
    }
open_list = []
close_list = []

class Box():
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = white
        self.x, self.y = self.get_coordinate(self.row, self.col)
        self.h_score = 0
        self.g_score = 0
        self.f_score = float("inf")
        self.parent = None

    def make_start(self):
        self.color = color_dict["start"]
    
    def make_end(self):
        self.color = color_dict["end"]

    def make_barrier(self):
        self.color = color_dict["barrier"]

    def make_path(self):
        self.color = color_dict["path"]
    
    def make_open(self):
        self.color = color_dict["open"]
    
    def make_close(self):
        self.color = color_dict["close"]

    def make_reset(self):
        self.color = color_dict["idle"]

    def get_coordinate(self, row, col):
        return col*box_size, row*box_size
    
    def calc_dist(self, box1, box2):
        dist = math.sqrt((box2.row-box1.row)**2 + (box2.col-box1.col)**2)
        return dist
    
    def is_traversable(self):
        if self.color == color_dict["barrier"]:
            return False
        return True 

    def update_score(self, parent, end):
        h = self.calc_dist(self, end)
        g = self.calc_dist(self, parent) + parent.g_score
        f = g+h
        self.h = h
        if f < self.f_score:
            self.f_score = f
            self.g_score = g
            self.parent = parent
    
    def find_neighbour(self, grid):
        neighbour_list = []
        for i in range(-1, 2):
            for j in range(-1,2):
                row = self.row + i
                col = self.col + j
                if row != self.row and col != self.col:
                    continue
                if row >=n or col>=n or row<0 or col<0:
                    continue
                if i == 0 and j == 0:
                    continue
                if(grid[row][col].is_traversable() and (grid[row][col] not in close_list)):
                    neighbour_list.append(grid[row][col])
        return neighbour_list

    def draw_box(self):
        pygame.draw.rect(screen, self.color, (self.x+1, self.y+1, box_size-1, box_size-1))

class Grid():
    def __init__(self):
        self.start = None
        self.end = None
        self.mouse_selec = None
        self.mouse_clicked = 0
        self.grid = [[Box(row, col) for col in range(n)] for row in range(n)]
    
    def draw_grid(self):
        for i in range(n+1):
            pygame.draw.line(screen, grey, (0,i*box_size), (screen_width, i*box_size), 1)
            pygame.draw.line(screen, grey, (i*box_size, 0), (i*box_size, box_size*n), 1)
    
    def get_rowCol(self, x, y):
        col = x//box_size
        row = y//box_size
        col = 0 if col<0 else n-1 if col>=n else col
        row = 0 if row<0 else n-1 if row>=n else row
        return row, col
    
    def get_min_Fscore(self):
        min = float("inf")
        current = None
        for box in open_list:
            if box.f_score < min:
                min = box.f_score
                current = box
        return current 

    def update_box_status(self, x, y):
        row, col = self.get_rowCol(x, y)
        box = self.grid[row][col]

        if box == self.start:
            self.start = None
        
        if box == self.end:
            self.end = None
        
        if self.mouse_selec:
            if self.mouse_selec == "start" and self.start:
                self.start.make_reset()
                self.start = box 
                box.make_start()
            elif self.mouse_selec == "start":
                self.start = box 
                box.make_start()
            elif self.mouse_selec == "end" and self.end:
                self.end.make_reset()
                self.end = box 
                box.make_end()
            elif self.mouse_selec == "end":
                self.end = box
                box.make_end()
            else:
                box.make_barrier()
    
    def find_shortest_path(self):
        if(not self.start or not self.end):
            return 1
        start = self.start
        end = self.end
        start.g_score = 0
        start.h_score = start.calc_dist(start, end)
        start.f_score = start.h_score + start.g_score
        open_list.append(start)
        current = start
        neighbour_list = current.find_neighbour(self.grid)
        print(neighbour_list)

        while (current != end):
            current = self.get_min_Fscore()
            open_list.remove(current)
            close_list.append(current)

            if current == end:
                self.display_path()
                return 1

            if current != start and current != end:
                current.make_close()
            
            neighbour_list = current.find_neighbour(self.grid)
            for neighbour in neighbour_list:
                if(neighbour.is_traversable() and neighbour not in close_list):
                    neighbour.update_score(current, end)
                if neighbour not in open_list:
                    open_list.append(neighbour)
                if neighbour != start and neighbour != end:
                    neighbour.make_open()
            self.update_screen()

    def display_path(self):
        end = self.end
        start = self.start
        current = end
        
        while (current != start):
            if current != end and current != start:
                current.make_path()
            current= current.parent
            self.update_screen()
    
    def reset_grid(self):
        for row in self.grid:
            for box in row:
                box.make_reset()
                box.f_score = float("inf")
        self.mouse_selec = None
        self.start = None
        self.end = None
        open_list = []
        close_list = []

    def update_screen(self):
        self.draw_grid()
        for row in self.grid:
            for box in row:
                box.draw_box()
        pygame.display.update()
        pygame.event.pump()

##############################################################
grid = Grid()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                grid.mouse_selec = "start"
            elif event.key == pygame.K_e:
                grid.mouse_selec = "end"
            elif event.key == pygame.K_b:
                grid.mouse_selec = "barrier"
            elif event.key == pygame.K_SPACE:
                grid.find_shortest_path()
            elif event.key == pygame.K_r:
                grid.reset_grid()
        if event.type == pygame.MOUSEBUTTONDOWN:
            grid.mouse_clicked = 1
        if event.type == pygame.MOUSEBUTTONUP:
            grid.mouse_clicked = 0
        if grid.mouse_clicked == 1:
            x, y = pygame.mouse.get_pos()
            grid.update_box_status(x,y)
            
    grid.update_screen()

