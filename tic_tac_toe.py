import pygame
from datetime import datetime
import os
from pygame.locals import *
from sys import exit as off
import socket
import json
import threading
import random
import copy

pygame.init()


# tworzenie okna
wysokosc = 300
szerokosc = 300
rozmiary_okna = ((wysokosc, szerokosc))
screen = pygame.display.set_mode(rozmiary_okna)
pygame.display.set_caption('Kółko i krzyżyk')

# kolor
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

# szukanie gdzie jest plik
file_place = os.path.dirname(__file__)
# obrazki
iks = pygame.image.load(file_place + r"\pngs\sym_x.png").convert_alpha()
kolko = pygame.image.load(file_place + r"\pngs\sym_o.png").convert_alpha()
# czcionka
font = pygame.font.SysFont(None, 40)

clicked = False
gracz = 1
mouse = (0,0)
znaczniki = []
wygrany = 0
lista_wynikow = []
wygrane_X = 0
wygrane_O = 0
menu = "start"
start_visible = False
bot = 0

szerokosc_linii = 4

# prostokąt do przycisku 'ponownej gry'
again_rect = Rect(szerokosc // 2 - 100, wysokosc // 2, 200, 40)
# prostokąt do przycisku 'wyjdz'
wyjdz_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 + 50, 200, 40)
# prostokąt do przycisku 'wyjdz' w poczekalni
wyjdz_pocz_rect = Rect(szerokosc - 110, wysokosc - 50, 100, 40)
# prostokąt do przycisku 'gry offline'
offline_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 - 60, 200, 40)
# prostokąt do przycisku 'gry z botem'
solo_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 - 10, 200, 40)
# prostokąt do przycisku 'gry online'
online_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 + 40, 200, 40)
# prostokąt do przycisku 'stworz gre'
stworz_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 - 60, 200, 40)
# prostokąt do przycisku 'dolacz'
dolacz_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 - 10, 200, 40)
# prostokąt do przycisku 'dolacz losowo'
losowo_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 + 40, 200, 40)
# prostokąt do przycisku 'start'
start_rect = Rect(szerokosc // 2 - 100, wysokosc // 2, 200, 40)
# prostokąt do przycisku 'latwy'
latwy_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 - 60, 200, 40)
# prostokąt do przycisku 'sredni'
sredni_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 - 10, 200, 40)
# prostokąt do przycisku 'trudny'
trudny_rect = Rect(szerokosc // 2 - 100, wysokosc // 2 + 40, 200, 40)

# plansza 3x3
for x in range (3):
	row = [0] * 3
	znaczniki.append(row)

class Online():
	def __init__(self):
		self.server = socket.gethostname()
		self.port = 5000
		self.client_socket = None
		self.code = "0000"
		self.join_code = ""
		self.host = False
		self.krzyzyk = "Oczekiwanie"
		self.kolko = "Oczekiwanie"
		self.player = 1
		self.ruch = False
		self.result = None
		self.d = None
	
	def connect(self):
		self.client_socket = socket.socket()
		try:
			self.client_socket.connect((self.server, self.port))
		except:
			return False
		packet = {"type":"status"}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())

		data = self.client_socket.recv(2048).decode()
		data = json.loads(data)
		if data["status"] == 0: # OK
			gd = threading.Thread(target=self.get_data)
			gd.start()
			return True
		else:
			return False
		return True

	def get_data(self):
		while True:
			data = self.client_socket.recv(2048).decode()
			if not data:
				break
			data = json.loads(data)
			dt = data["type"]
			global menu
			global znaczniki
			if dt == "create_game":
				self.d = data
			elif dt == "join_game":
				self.d = data
			elif dt == "join_random_game":
				self.d = data
			elif dt == "player_joined":
				if data["player"] == "O":
					self.kolko = "Przeciwnik"
				else:
					self.krzyzyk = "Przeciwnik"
			elif dt == "start_game":
				self.d = data
			elif dt == "game_started":
				menu = "gra_online"
			elif dt == "move":
				self.d = data
			elif dt == "player_moved":
				field = data["field"]
				column = field % 3
				row = field // 3
				znaczniki[column][row] = "OLX".index(data["player"])-1
				self.ruch = True
			elif dt == "game_ended":
				self.ruch = False
				self.krzyzyk = "Ekran końcowy"
				self.kolko = "Ekran końcowy"
				self.result = data["result"]
				menu = "online_koniec_gry"
			elif dt == "ready":
				self.d = data
			elif dt == "player_ready":
				player = data["player"]
				you = "OLX"[self.player+1]
				if player == "X":
					self.krzyzyk = "Przeciwnik"
					if player == you:
						self.krzyzyk = "Ty"
				else:
					self.kolko = "Przeciwnik"
					if player == you:
						self.kolko = "Ty"
			elif dt == "player_left":
				znaczniki = []
				for x in range (3):
					row = [0] * 3
					znaczniki.append(row)
				menu = "poczekalnia"
				player = data["player"]
				if player == "X":
					self.krzyzyk = "Oczekiwanie"
					self.kolko = "Ty"
				else:
					self.kolko = "Oczekiwanie"
					self.krzyzyk = "Ty"
				self.ruch = False
				self.host = True

	def wait_for_data(self):
		while True:
			if self.d != None:
				d = self.d
				self.d = None
				return d

	def create_game(self):
		packet = {"type":"create_game"}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())
		
		data = self.wait_for_data()
		if data["status"] == 0:
			self.code = data["code"]
			self.player = 1
			self.krzyzyk = "Ty"
			return True
		else:
			return False

	def join_game(self):
		packet = {"type":"join_game", "code":self.join_code}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())

		data = self.wait_for_data()
		if data["status"] == 0:
			self.code = self.join_code
			self.join_code = ""
			self.host = False
			self.krzyzyk = "Przeciwnik"
			self.kolko = "Ty"
			self.player = -1
			if data["player"] == "X":
				self.krzyzyk = "Ty"
				self.kolko = "Przeciwnik"
				self.player = 1
			return True
		else:
			return False

	def join_random_game(self):
		packet = {"type":"join_random_game"}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())

		data = self.wait_for_data()
		if data["status"] == 0:
			self.code = data["code"]
			self.join_code = ""
			self.host = False
			self.krzyzyk = "Przeciwnik"
			self.kolko = "Ty"
			self.player = -1
			if data["player"] == "X":
				self.krzyzyk = "Ty"
				self.kolko = "Przeciwnik"
				self.player = 1
			return True
		else:
			return False

	def start_game(self):
		packet = {"type":"start_game"}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())

		data = self.wait_for_data()
		if data["status"] == 0:
			self.ruch = True
			return True
		return False

	def move(self, field):
		packet = {"type":"move", "field": field}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())

		data = self.wait_for_data()
		if data["status"] == 0:
			self.ruch = False
			return True
		return False

	def ready(self):
		packet = {"type":"ready"}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())

		data = self.wait_for_data()
		if data["status"] == 0:
			return True
		return False

	def leave(self):
		packet = {"type":"leave"}
		packet = json.dumps(packet)
		self.client_socket.send(packet.encode())
		self.client_socket = None
		self.code = "0000"
		self.join_code = ""
		self.host = False
		self.krzyzyk = "Oczekiwanie"
		self.kolko = "Oczekiwanie"
		self.player = 1
		self.ruch = False
		self.result = None
		self.d = None

online = Online()

def wolne(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return True
    return False

def ocen(b) :
    for row in range(3) :    
        if b[row][0] == b[row][1] and b[row][1] == b[row][2]:       
            if b[row][0] == -1:
                return 10
            elif b[row][0] == 1:
                return -10
    for col in range(3) :
        if b[0][col] == b[1][col] and b[1][col] == b[2][col]:
            if b[0][col] == -1:
                return 10
            elif b[0][col] == 1:
                return -10
    if (b[0][0] == b[1][1] and b[1][1] == b[2][2]):
        if b[0][0] == -1:
            return 10
        elif b[0][0] == 1:
            return -10
 
    if b[0][2] == b[1][1] and b[1][1] == b[2][0]:
        if b[0][2] == -1:
            return 10
        elif b[0][2] == 1:
            return -10
 
    return 0

def minimax(board, gl, m) :
	wynik = ocen(board)
	if wynik == 10:
		return wynik
	if wynik == -10:
		return wynik
	if wolne(board) == False:
		return 0
	if m:    
		best = -1000
		for i in range(3):        
			for j in range(3):
				if board[i][j]==0:
					board[i][j] = -1
					best = max(best, minimax(board, gl+1, not m))
					board[i][j] = 0
		return best
	else:
		best = 1000
		for i in range(3) :        
			for j in range(3) :
				if board[i][j] == 0:
					board[i][j] = 1
					best = min(best, minimax(board, gl + 1, not m))
					board[i][j] = 0
		return best

def ruch_bota(poziom):
	global znaczniki
	if not wolne(znaczniki):
		return
	def check_board(board):
		board = [board[f%3][f//3] for f in range(9)]
		for row in range(3):
			if board[row*3] != 0:
				if board[row*3] == board[row*3+1] == board[row*3+2]:
					return (True, board[row*3])
		for col in range(3):
			if board[col] != 0:
				if board[col] == board[col+3] == board[col+6]:
					return (True, board[col])
		if board[2] == board[4] == board[6] and board[4] != 0:
			return (True, board[4])
		if board[0] == board[4] == board[8] and board[4] != 0:
			return (True, board[4])
		if not 0 in board:
			return (True, 0)
		return (False, False)
	
	if poziom == 1:
		mozliwe = []
		for y in range(3):
			for x in range(3):
				if znaczniki[y][x] == 0:
					mozliwe.append([y, x])
		if len(mozliwe) > 0:
			wybor = random.choice(mozliwe)
			znaczniki[wybor[0]][wybor[1]] = -1
			return
		return
	elif poziom == 2:
		for j in range(2):
			for y in range(3):
				for x in range(3):
					if znaczniki[y][x] == 0:
						nowe_znaczniki = copy.deepcopy(znaczniki)
						g = -1
						if j == 1:
							g = 1
						nowe_znaczniki[y][x] = g
						wynik = check_board(nowe_znaczniki)
						if wynik[0]:
							if wynik[1] == g:
								znaczniki[y][x] = -1
								return
		ruch_bota(1)
		return
	elif poziom == 3:
		naj = -1000
		bestMove = (-1, -1)
		nowe_znaczniki = copy.deepcopy(znaczniki)
		for i in range(3):
			for j in range(3):
				if znaczniki[i][j] == 0:
					nowe_znaczniki[i][j] = -1
					ruch = minimax(nowe_znaczniki, 0, False)
					nowe_znaczniki[i][j] = 0
					if ruch > naj:
						najruch = (i, j)
						naj = ruch
		znaczniki[najruch[0]][najruch[1]] = -1
		return
					

def rysuj_plansza():
	# kolor tła
	bg = (255, 255, 255)
	# kolor linii
	grid = (0, 0, 0)
	screen.fill(bg)
	for x in range(1,3):
		pygame.draw.line(screen, grid, (0, 100 * x), (szerokosc, 100 * x), szerokosc_linii)
		pygame.draw.line(screen, grid, (100 * x, 0), (100 * x, wysokosc), szerokosc_linii)

def rysuj_symbol():
	x_pos = 0
	for x in znaczniki:
		y_pos = 0
		for y in x:
			if y == 1:
				screen.blit(iks, (x_pos * 100 + 1, y_pos * 100))
			if y == -1:
				screen.blit(kolko, (x_pos * 100 + 1, y_pos * 100))
			y_pos += 1
		x_pos += 1

def rysuj_ruch():
	if online.ruch == True:
		kod_txt = font.render("Twój ruch!", True, blue)
		screen.blit(kod_txt, (szerokosc // 2 - 65, 10))


def czy_koniec_gry():
	global menu
	global wygrany

	x_pos = 0
	for x in znaczniki:
		# sprawdzanie kolumn
		if sum(x) == 3:
			wygrany = 1
			menu = "koniec_gry"
		if sum(x) == -3:
			wygrany = 2
			menu = "koniec_gry"
		# sprawdzanie wierszy
		if znaczniki[0][x_pos] + znaczniki[1][x_pos] + znaczniki[2][x_pos] == 3:
			wygrany = 1
			menu = "koniec_gry"
		if znaczniki[0][x_pos] + znaczniki[1][x_pos] + znaczniki[2][x_pos] == -3:
			wygrany = 2
			menu = "koniec_gry"
		x_pos += 1

	# czy wygrany: krzyżyk
	if znaczniki[0][0] + znaczniki[1][1] + znaczniki[2][2] == 3 or znaczniki[2][0] + znaczniki[1][1] + znaczniki[0][2] == 3:
		wygrany = 1
		menu = "koniec_gry"
	# czy wygrany: kółko
	if znaczniki[0][0] + znaczniki[1][1] + znaczniki[2][2] == -3 or znaczniki[2][0] + znaczniki[1][1] + znaczniki[0][2] == -3:
		wygrany = 2
		menu = "koniec_gry"

	# czy remis
	if menu != "koniec_gry":
		tie = True
		for row in znaczniki:
			for i in row:
				if i == 0:
					tie = False
		if tie == True:
			menu = "koniec_gry"
			wygrany = 0

def rysuj_menu_poczatkowe():
	tryb_img = font.render(" Wybierz tryb", True, (0, 0, 0))
	pygame.draw.rect(screen, (150, 0, 0), (szerokosc // 2 - 100, wysokosc // 2 - 120, 200, 50))
	screen.blit(tryb_img, (szerokosc // 2 - 100, wysokosc // 2 - 110))

	offline_text = '   Graj offline'
	offline_img = font.render(offline_text, True, white)
	pygame.draw.rect(screen, red, offline_rect)
	screen.blit(offline_img, (szerokosc // 2 - 100, wysokosc // 2 - 50))

	solo_text = '  Graj z botem'
	solo_img = font.render(solo_text, True, white)
	pygame.draw.rect(screen, red, solo_rect)
	screen.blit(solo_img, (szerokosc // 2 - 100, wysokosc // 2))

	online_text = '   Graj online'
	online_img = font.render(online_text, True, white)
	pygame.draw.rect(screen, red, online_rect)
	screen.blit(online_img, (szerokosc // 2 - 100, wysokosc // 2 + 50))

def rysuj_menu_online():
	stworz_text = "    Stwórz grę"
	stworz_img = font.render(stworz_text, True, white)
	pygame.draw.rect(screen, red, stworz_rect)
	screen.blit(stworz_img, (szerokosc // 2 - 100, wysokosc // 2 - 50))

	dolacz_text = ' Dołącz do gry'
	dolacz_img = font.render(dolacz_text, True, white)
	pygame.draw.rect(screen, red, dolacz_rect)
	screen.blit(dolacz_img, (szerokosc // 2 - 100, wysokosc // 2))

	losowo_text = 'Dołącz losowo'
	losowo_img = font.render(losowo_text, True, white)
	pygame.draw.rect(screen, red, losowo_rect)
	screen.blit(losowo_img, (szerokosc // 2 - 100, wysokosc // 2 + 50))

def rysuj_dolacz():
	kod_txt = font.render("Kod: " + online.join_code, True, red)
	screen.blit(kod_txt, (10, wysokosc-30))
	i = 0
	for y in range(3):
		for x in range(3):
			i += 1
			liczba = font.render(str(i), True, red)
			screen.blit(liczba, (43+x*100, 37+y*100))
	
def rysuj_poczekalnie():
	global start_visible
	start_visible = False
	krzyzyk_txt = font.render("X: " + online.krzyzyk, True, red)
	screen.blit(krzyzyk_txt, (10, 10))

	kolko_txt = font.render("O: " + online.kolko, True, red)
	screen.blit(kolko_txt, (10, 40))
	
	kod_txt = font.render("Kod: " + online.code, True, red)
	screen.blit(kod_txt, (10, wysokosc-30))

	wyjdz_pocz_text = 'Wyjdź'
	wyjdz_pocz_img = font.render(wyjdz_pocz_text, True, white)
	pygame.draw.rect(screen, red, wyjdz_pocz_rect)
	screen.blit(wyjdz_pocz_img, (szerokosc - 103, wysokosc - 40))

	if online.host:
		if online.kolko not in ["Oczekiwanie", "Ekran końcowy"] and online.krzyzyk not in ["Oczekiwanie", "Ekran końcowy"]:
			start_visible = True
			start_text = '        Start!'
			start_img = font.render(start_text, True, white)
			pygame.draw.rect(screen, red, start_rect)
			screen.blit(start_img, (szerokosc // 2 - 98, wysokosc // 2 + 10))

def rysuj_poziom_bota():
	latwy_text = "       Łatwy"
	latwy_img = font.render(latwy_text, True, white)
	pygame.draw.rect(screen, red, latwy_rect)
	screen.blit(latwy_img, (szerokosc // 2 - 100, wysokosc // 2 - 50))

	sredni_text = '       Średni'
	sredni_img = font.render(sredni_text, True, white)
	pygame.draw.rect(screen, red, sredni_rect)
	screen.blit(sredni_img, (szerokosc // 2 - 100, wysokosc // 2))

	trudny_text = '       Trudny'
	trudny_img = font.render(trudny_text, True, white)
	pygame.draw.rect(screen, red, trudny_rect)
	screen.blit(trudny_img, (szerokosc // 2 - 100, wysokosc // 2 + 50))

def rysuj_koniec_gry(wygrany):

	if wygrany != 0:
		end_text = "Gracz " + str(wygrany) + " wygrał"

	elif wygrany == 0:
		end_text = "Remis!"

	end_img = font.render(end_text, True, white)
	pygame.draw.rect(screen, red, (szerokosc // 2 - 100, wysokosc // 2 - 60, 200, 50))
	screen.blit(end_img, (szerokosc // 2 - 100, wysokosc // 2 - 50))

	again_text = 'Graj ponownie'
	again_img = font.render(again_text, True, white)
	pygame.draw.rect(screen, red, again_rect)
	screen.blit(again_img, (szerokosc // 2 - 98, wysokosc // 2 + 10))

	wyjdz_text = '        Wyjdź'
	wyjdz_img = font.render(wyjdz_text, True, white)
	pygame.draw.rect(screen, red, wyjdz_rect)
	screen.blit(wyjdz_img, (szerokosc // 2 - 100, wysokosc // 2 + 60))


wybrane_menu = "offline"
# main loop
running = True
while running:

	# rysuje planszę i znaczniki (symbole)
	rysuj_plansza()
	rysuj_symbol()
	rysuj_ruch()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			if online.client_socket != None:
				online.client_socket.close()
		if menu == "offline":
			if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
				clicked = True
			if event.type == pygame.MOUSEBUTTONUP and clicked == True:
				clicked = False
				mouse = pygame.mouse.get_pos()
				column = mouse[0] // 100
				row = mouse[1] // 100
				if znaczniki[column][row] == 0:
					znaczniki[column][row] = gracz
					gracz *= -1
					czy_koniec_gry()
		if menu == "solo":
			if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
				clicked = True
			if event.type == pygame.MOUSEBUTTONUP and clicked == True:
				clicked = False
				mouse = pygame.mouse.get_pos()
				column = mouse[0] // 100
				row = mouse[1] // 100
				if znaczniki[column][row] == 0:
					znaczniki[column][row] = gracz
					ruch_bota(bot)
					czy_koniec_gry()

	if menu == "start":
		rysuj_menu_poczatkowe()
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			if offline_rect.collidepoint(mouse):
				# gra przeciwko komus na jednym komputerze
				bot = 0
				menu = "offline"
				wybrane_menu = "offline"
			if solo_rect.collidepoint(mouse):
				# gra z botem
				menu = "poziom_bota"
				wybrane_menu = "solo"
			if online_rect.collidepoint(mouse):
				# gra online
				if online.connect():
					menu = "menu_online"
				else:
					# Nie polaczylo z serwerem
					pygame.quit()

	if menu == "poziom_bota":
		rysuj_poziom_bota()
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			if latwy_rect.collidepoint(mouse):
				bot = 1
				gracz = 1
				menu = "solo"
			if sredni_rect.collidepoint(mouse):
				bot = 2
				gracz = 1
				menu = "solo"
			if trudny_rect.collidepoint(mouse):
				bot = 3
				gracz = 1
				menu = "solo"

	if menu == "menu_online":
		rysuj_menu_online()
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			if stworz_rect.collidepoint(mouse):
				if online.create_game() == False:
					continue
				online.host = True
				menu = "poczekalnia"
			elif dolacz_rect.collidepoint(mouse):
				online.host = False
				online.join_code = ""
				menu = "dolacz"
			elif losowo_rect.collidepoint(mouse):
				if online.join_random_game():
					online.host = False
					menu = "poczekalnia"

	if menu == "dolacz":
		rysuj_dolacz()
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			x = (mouse[0] // 100) + 1
			y = (mouse[1] // 100) + 1
			wybrane = y*3+x-3
			online.join_code += str(wybrane)
			if len(online.join_code) == 4:
				if online.join_game():
					menu = "poczekalnia"
				else:
					menu = "menu_online"

	if menu == "poczekalnia":
		rysuj_poczekalnie()
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			if start_rect.collidepoint(mouse) and online.host and start_visible:
				online.start_game()
			elif wyjdz_pocz_rect.collidepoint(mouse):
				menu = "start"
				online.leave()

	if menu == "gra_online":
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			column = mouse[0] // 100
			row = mouse[1] // 100
			pole = row*3+column
			if online.move(pole):
				znaczniki[column][row] = online.player

	if menu == "online_koniec_gry":
		rysuj_koniec_gry(online.result)
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			if again_rect.collidepoint(mouse):
				if online.ready():
					menu = "poczekalnia"
					mouse = (0,0)
					znaczniki = []
					wygrany = 0
					for x in range (3):
						row = [0] * 3
						znaczniki.append(row)
			elif wyjdz_rect.collidepoint(mouse):
				online.leave()
				znaczniki = []
				for x in range (3):
					row = [0] * 3
					znaczniki.append(row)
				menu = "start"
				

	if menu == "koniec_gry":
		rysuj_koniec_gry(wygrany)
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			mouse = pygame.mouse.get_pos()
			if again_rect.collidepoint(mouse):
				# resetowanie planszy
				menu = wybrane_menu
				mouse = (0,0)
				znaczniki = []
				# zmiana kolejności, jeżeli wygrał X to zaczyna O i na odwrót
				if wygrany == 1:
					wygrane_X += 1
					if menu == "offline":
						gracz = -1
					lista_wynikow.append('Wygral: X')
				elif wygrany == 2:
					wygrane_O += 1
					if menu == "offline":
						gracz = 1
					lista_wynikow.append('Wygral: O')
				wygrany = 0
				for x in range (3):
					row = [0] * 3
					znaczniki.append(row)
			elif wyjdz_rect.collidepoint(mouse):
				# resetowanie planszy
				menu = "start"
				mouse = (0,0)
				znaczniki = []
				# zmiana kolejności, jeżeli wygrał X to zaczyna O i na odwrót
				if wygrany == 1:
					wygrane_X += 1
					if menu == "offline":
						gracz = -1
					lista_wynikow.append('Wygral: X')
				elif wygrany == 2:
					wygrane_O += 1
					if menu == "offline":
						gracz = 1
					lista_wynikow.append('Wygral: O')
				wygrany = 0
				for x in range (3):
					row = [0] * 3
					znaczniki.append(row)

	pygame.display.flip()
# zapisywanie wyników w folderze, w którym znajduje się plik (nazywa go datą i godziną wyłączenia programu)

if wygrane_X > 0 or wygrane_O > 0:
	now = datetime.now()
	current_datetime = datetime.now()
	str_current_datetime = now.strftime("\%Y.%m.%d_%H;%M;%S")
	file_output = file_place + '\wyniki' + str_current_datetime + ".txt"
	file_name = str_current_datetime + ".txt"

	f = open(file_output, 'w')
	for element in lista_wynikow:
		f.write(f'{element}\n')

	f.write(f'Ilosc wygranych X: {wygrane_X}\n')
	f.write(f'Ilosc wygranych O: {wygrane_O}')
	f.close()

pygame.quit()
