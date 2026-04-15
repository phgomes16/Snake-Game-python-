import turtle
import random
import time
import numpy as np
import pygame

# ── Som (beeps gerados via numpy + pygame) ────────────────────────
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=256)

def gerar_beep(freq, duracao, volume=0.4):
    """Gera e toca um tom puro (onda quadrada, estilo Nokia)."""
    amostras = int(44100 * duracao)
    t = np.linspace(0, duracao, amostras, endpoint=False)
    onda = np.sign(np.sin(2 * np.pi * freq * t))  # onda quadrada
    onda = (onda * volume * 32767).astype(np.int16)
    # Se o mixer estiver em estéreo, duplica o canal
    if pygame.mixer.get_init()[2] == 2:
        onda = np.column_stack((onda, onda))
    som = pygame.sndarray.make_sound(onda)
    som.play()

def som_comer():
    """Dois beeps ascendentes curtos — comer a comida."""
    gerar_beep(880, 0.045)
    time.sleep(0.05)
    gerar_beep(1320, 0.045)

def som_gameover():
    """Sequência descendente — morte da cobra."""
    for freq in [523, 392, 330, 262]:
        gerar_beep(freq, 0.12)
        time.sleep(0.13)

# ── Paleta Nokia LCD ──────────────────────────────────────────────
COR_FUNDO    = "#8B9E6B"   # verde-LCD apagado
COR_ESCURA   = "#2C3A1E"   # verde muito escuro (pixels ativos)
COR_GRADE    = "#7D9060"   # linhas suaves de grade
COR_BORDA    = "#4A5C30"   # borda interna da tela

LARGURA_TELA = 560
ALTURA_TELA  = 620
MARGEM       = 40          # área de HUD (placar) no topo
TAMANHO_JOGO = 480         # área quadrada do jogo
CELULA       = 16          # tamanho de cada "pixel"
COLUNAS      = TAMANHO_JOGO // CELULA   # 30
LINHAS       = TAMANHO_JOGO // CELULA   # 30

# Offset para centralizar a grade na tela
OX = -TAMANHO_JOGO // 2   # -240
OY = -TAMANHO_JOGO // 2 - (MARGEM // 2)  # -260

# ── Tela ──────────────────────────────────────────────────────────
tela = turtle.Screen()
tela.title("SNAKE  |  Nokia Edition")
tela.bgcolor("#5A6B3A")    # moldura externa
tela.setup(width=LARGURA_TELA, height=ALTURA_TELA)
tela.tracer(0)

# ── Utilitário: converter grade → pixels turtle ────────────────────
def grade_para_tela(col, lin):
    x = OX + col * CELULA + CELULA // 2
    y = OY + lin * CELULA + CELULA // 2
    return x, y

# ── Desenhista de blocos (reutilizável) ───────────────────────────
desenhista = turtle.Turtle()
desenhista.hideturtle()
desenhista.penup()
desenhista.speed(0)

def desenhar_bloco(col, lin, cor, tamanho=CELULA - 2):
    """Desenha um quadradinho cheio na posição da grade."""
    x, y = grade_para_tela(col, lin)
    desenhista.goto(x - tamanho // 2, y - tamanho // 2)
    desenhista.pendown()
    desenhista.fillcolor(cor)
    desenhista.pencolor(cor)
    desenhista.begin_fill()
    for _ in range(4):
        desenhista.forward(tamanho)
        desenhista.left(90)
    desenhista.end_fill()
    desenhista.penup()

def limpar_bloco(col, lin):
    """Apaga um bloco (pinta com a cor de fundo)."""
    desenhar_bloco(col, lin, COR_FUNDO, tamanho=CELULA)

# ── Desenhar fundo LCD com grade ──────────────────────────────────
fundo = turtle.Turtle()
fundo.hideturtle()
fundo.penup()
fundo.speed(0)

def desenhar_fundo():
    # Retângulo LCD
    fundo.goto(OX, OY)
    fundo.pendown()
    fundo.fillcolor(COR_FUNDO)
    fundo.pencolor(COR_BORDA)
    fundo.pensize(3)
    fundo.begin_fill()
    for _ in range(2):
        fundo.forward(TAMANHO_JOGO)
        fundo.left(90)
        fundo.forward(TAMANHO_JOGO)
        fundo.left(90)
    fundo.end_fill()
    fundo.penup()



desenhar_fundo()

# ── HUD (placar estilo Nokia) ─────────────────────────────────────
hud = turtle.Turtle()
hud.hideturtle()
hud.penup()
hud.color(COR_ESCURA)

pontos  = 0
recorde = 0

def atualizar_hud():
    hud.clear()
    hud.goto(-230, TAMANHO_JOGO // 2 - (MARGEM // 2) + 8)
    hud.write(f"SCORE:{pontos:04d}", font=("Courier", 13, "bold"))
    hud.goto(60,  TAMANHO_JOGO // 2 - (MARGEM // 2) + 8)
    hud.write(f"BEST:{recorde:04d}",  font=("Courier", 13, "bold"))

atualizar_hud()

# ── Estado do jogo ────────────────────────────────────────────────
# Cobra representada como lista de (col, lin)
cobra     = [(15, 15), (14, 15), (13, 15)]
direcao   = "direita"
prox_dir  = "direita"
delay     = 0.10
rodando   = True

def nova_comida():
    while True:
        c = random.randint(0, COLUNAS - 1)
        l = random.randint(0, LINHAS - 1)
        if (c, l) not in cobra:
            return (c, l)

comida = nova_comida()

# Desenha estado inicial
for seg in cobra:
    desenhar_bloco(seg[0], seg[1], COR_ESCURA)
desenhar_bloco(comida[0], comida[1], COR_ESCURA, tamanho=8)  # comida menor
tela.update()

# ── Controles ─────────────────────────────────────────────────────
def p_cima():
    global prox_dir
    if direcao != "baixo": prox_dir = "cima"
def p_baixo():
    global prox_dir
    if direcao != "cima":  prox_dir = "baixo"
def p_esq():
    global prox_dir
    if direcao != "direita": prox_dir = "esquerda"
def p_dir():
    global prox_dir
    if direcao != "esquerda": prox_dir = "direita"

tela.listen()
tela.onkey(p_cima,  "Up");    tela.onkey(p_cima,  "w")
tela.onkey(p_baixo, "Down");  tela.onkey(p_baixo, "s")
tela.onkey(p_esq,   "Left");  tela.onkey(p_esq,   "a")
tela.onkey(p_dir,   "Right"); tela.onkey(p_dir,   "d")

# ── Tela de Game Over ─────────────────────────────────────────────
gameover_t = turtle.Turtle()
gameover_t.hideturtle()
gameover_t.penup()
gameover_t.color(COR_ESCURA)

aguardando_tecla = False

def continuar_apos_gameover():
    global aguardando_tecla
    aguardando_tecla = False

def mostrar_gameover():
    global aguardando_tecla
    aguardando_tecla = True
    gameover_t.goto(0, 40)
    gameover_t.write("GAME OVER", align="center", font=("Courier", 18, "bold"))
    gameover_t.goto(0, 10)
    gameover_t.write(f"SCORE: {pontos}", align="center", font=("Courier", 13, "bold"))
    gameover_t.goto(0, -15)
    gameover_t.write("press any key", align="center", font=("Courier", 10, "normal"))
    tela.update()

    # Qualquer tecla desfaz o aguardo
    for tecla in ["Up","Down","Left","Right","w","a","s","d",
                  "space","Return","Escape"]:
        tela.onkey(continuar_apos_gameover, tecla)

    # Aguarda até tecla ser pressionada
    while aguardando_tecla:
        tela.update()
        time.sleep(0.05)

    # Restaura os controles normais
    tela.onkey(p_cima,  "Up");    tela.onkey(p_cima,  "w")
    tela.onkey(p_baixo, "Down");  tela.onkey(p_baixo, "s")
    tela.onkey(p_esq,   "Left");  tela.onkey(p_esq,   "a")
    tela.onkey(p_dir,   "Right"); tela.onkey(p_dir,   "d")
    gameover_t.clear()

# ── Loop principal ────────────────────────────────────────────────
while True:
    tela.update()
    direcao = prox_dir
    time.sleep(delay)

    # Calcular nova cabeça
    col, lin = cobra[0]
    if direcao == "cima":    lin += 1
    elif direcao == "baixo": lin -= 1
    elif direcao == "esquerda": col -= 1
    elif direcao == "direita":  col += 1

    # Colisão com parede
    if col < 0 or col >= COLUNAS or lin < 0 or lin >= LINHAS:
        if pontos > recorde:
            recorde = pontos
        som_gameover()   # ← som de morte
        mostrar_gameover()
        # Reiniciar
        for seg in cobra:
            limpar_bloco(seg[0], seg[1])
        limpar_bloco(comida[0], comida[1])
        cobra    = [(15, 15), (14, 15), (13, 15)]
        direcao  = "direita"
        prox_dir = "direita"
        comida   = nova_comida()
        pontos   = 0
        delay    = 0.13
        for seg in cobra:
            desenhar_bloco(seg[0], seg[1], COR_ESCURA)
        desenhar_bloco(comida[0], comida[1], COR_ESCURA, tamanho=8)
        atualizar_hud()
        continue

    # Colisão com o próprio corpo
    if (col, lin) in cobra:
        if pontos > recorde:
            recorde = pontos
        som_gameover()   # ← som de morte
        mostrar_gameover()
        for seg in cobra:
            limpar_bloco(seg[0], seg[1])
        limpar_bloco(comida[0], comida[1])
        cobra    = [(15, 15), (14, 15), (13, 15)]
        direcao  = "direita"
        prox_dir = "direita"
        comida   = nova_comida()
        pontos   = 0
        delay    = 0.13
        for seg in cobra:
            desenhar_bloco(seg[0], seg[1], COR_ESCURA)
        desenhar_bloco(comida[0], comida[1], COR_ESCURA, tamanho=8)
        atualizar_hud()
        continue

    # Comeu a comida?
    comeu = (col, lin) == comida
    nova_cabeca = (col, lin)

    if comeu:
        limpar_bloco(comida[0], comida[1])
        cobra.insert(0, nova_cabeca)
        desenhar_bloco(nova_cabeca[0], nova_cabeca[1], COR_ESCURA)
        comida  = nova_comida()
        desenhar_bloco(comida[0], comida[1], COR_ESCURA, tamanho=8)
        pontos += 10
        som_comer()      # ← som de comer
        if delay > 0.05:
            delay -= 0.004
        atualizar_hud()
    else:
        # Remove cauda, adiciona cabeça
        cauda = cobra[-1]
        cobra.pop()
        cobra.insert(0, nova_cabeca)
        limpar_bloco(cauda[0], cauda[1])
        desenhar_bloco(nova_cabeca[0], nova_cabeca[1], COR_ESCURA)