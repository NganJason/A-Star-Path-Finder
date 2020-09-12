import pygame 
import math
import time

# Initialization
pygame.init()
screen_width = 800
screen_height = 800
# padding = 25
n = 50
box_size = (screen_width)// n
running = True 
screen = pygame.display.set_mode((screen_width, screen_height))

# Color code
white  = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (128, 0, 128)
red = (255, 0, 0)
black = (0, 0, 0)
orange = (255, 165 ,0)
turquoise = (64, 224, 208)
grey = (128, 128, 128)
color_dict = {"idle": white, "start": orange, "end": turquoise, "barrier": black, "close": red, "open": green, "path": purple}

class Grid():
    def __init__(self):
        self.grid = [[Box(row, col) for col in range(n)] for row in range(n)]
        self.color_boxes = []
        self.curr_selection = "idle"
        self.startEnd = {"start": None, "end": None}
        self.mouse = 0
        self.close_list = []
        self.open_list = []

    def draw_grid(self):
        for i in range(n + 1):
            pygame.draw.line(screen, grey, (0,i*box_size), (screen_width, i*box_size), 1)
            pygame.draw.line(screen, grey, (i*box_size, 0), (i*box_size, box_size*n), 1)
    
    def get_rowcol(self, x, y): 
        col = (x)//box_size
        row = (y)//box_size
        col = 0 if col<0 else n-1 if col>=n else col
        row = 0 if row<0 else n-1 if row>=n else row
        return row, col
    
    def get_min_Fscore(self):
        min = float("inf")
        next_box = None
        for box in self.open_list:
            if box.f_score < min:
                min = box.f_score
                next_box = box
        return next_box
    
    def find_neighbour(self, box):
        neighbour_list = []

        for i in range(-1,2):
            for j in range(-1,2):
                row = box.row + i
                col = box.col + j
                if row != box.row and col != box.col:
                    continue
                if row >= n or col >= n or row < 0 or col < 0:
                    continue
                elif i == 0 and j ==0:
                    continue
                elif(self.grid[row][col].is_box_traversable(self.close_list)):
                    neighbour_list.append(self.grid[row][col])
        return neighbour_list

    def update_box_status(self, x, y):
        row, col = self.get_rowcol(x,y)
        box = self.grid[row][col]

        selection = self.curr_selection
        if  box.status in self.startEnd:
            self.startEnd[box.status] = None

        if selection in self.startEnd and self.startEnd[selection] and self.startEnd[selection] != box:
            self.color_boxes.remove(self.startEnd[selection])
            self.startEnd[selection].status = "idle"
            self.startEnd[selection].color = color_dict["idle"]
            self.startEnd[selection] = box

        elif selection in self.startEnd:
            self.startEnd[selection] = box
            
        if selection != "idle" and box not in self.color_boxes:
            self.color_boxes.append(box)
        
        box.status = selection
        box.color = color_dict[selection]

    def update_open_close(self, box, status):
        box.color = color_dict[status]
        box.status = status
        if box not in self.color_boxes:
            self.color_boxes.append(box)
    
    def display_path(self):
        end = self.startEnd["end"]
        start = self.startEnd["start"]
        current = end
        while current!= start:
            if current != start and current != end:
                current.color = color_dict["path"]
            current = current.parent 
            # self.update_screen()


    def find_shortest_path(self):
        self.open_list = []
        self.close_list = []
        start = self.startEnd["start"]
        end = self.startEnd["end"]
        start.h_score = start.calc_dist(start, end)
        start.g_score = 0
        start.f_score = start.g_score + start.h_score
        self.open_list.append(start)
        current = start

        while (current != end):
            current = self.get_min_Fscore()

            self.open_list.remove(current)

            if current != start and current != end:
                self.update_open_close(current, "open")
            self.close_list.append(current)

            if current == end:
                self.display_path()
                return 1

            neighbour_list = self.find_neighbour(current)
            for neighbour in neighbour_list:
                if (neighbour.is_box_traversable(self.close_list)):
                    neighbour.update_score(current, end)
                if neighbour not in self.open_list:
                    self.open_list.append(neighbour)
                    if neighbour != start and neighbour != end:
                        self.update_open_close(neighbour, "close")
            # self.update_screen()
    
    def update_screen(self):
        screen.fill(white)
        
        for row in self.grid:
            for box in row:
                pygame.draw.rect(screen, box.color, (box.x+1, box.y+1, box_size-1, box_size-1))
        self.draw_grid()
        pygame.display.update()
        pygame.event.pump()
        

class Box():
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.status = "idle"
        self.color = white
        self.x, self.y = self.get_coordinate(self.row, self.col)
        self.h_score = 0
        self.g_score = 0
        self.f_score = float("inf")
        self.parent = None
        
    def get_coordinate(self, row, col):
        x =  col*box_size
        y = row*box_size
        return x,y
        
    def is_box_traversable(self, close_list):
        if self.status == "barrier" or self in close_list:
            return False
        return True

    def calc_dist(self, box1, box2):
        dist = math.sqrt((box2.row-box1.row)**2 + (box2.col-box1.col)**2)
        return dist
    
    def update_score(self, parent, end):
        h = self.calc_dist(self, end)
        g = self.calc_dist(self, parent) + parent.g_score
        f = h + g
        self.h_score = h
        if f < self.f_score:
            self.f_score = f
            self.g_score = g
            self.parent = parent
    
        
####################################################################
grid = Grid()
while running:
    grid.update_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                grid.curr_selection = "start"
            elif event.key == pygame.K_e:
                grid.curr_selection = "end"
            elif event.key == pygame.K_b:
                grid.curr_selection = "barrier"
            elif event.key == pygame.K_SPACE:
                grid.find_shortest_path()
        if event.type == pygame.MOUSEBUTTONDOWN:
            grid.mouse = 1
        if event.type == pygame.MOUSEBUTTONUP:
            grid.mouse = 0
        if grid.mouse == 1:
            x, y = pygame.mouse.get_pos()
            grid.update_box_status(x,y)
    # pygame.event.pump()
pygame.quit()
    
    