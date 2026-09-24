"""Tetris Mondrian — jogo didático em Python + Pygame.

Execute: python tetris_mondrian.py
Regras, desenho e entrada separados para facilitar o estudo no capítulo 6.
Todas as formas são desenhadas em código; não há imagens ou fontes externas.
"""
from dataclasses import dataclass
import random
import sys
import pygame

COLUNAS, LINHAS = 10, 20
CELULA = 28
LARGURA, ALTURA = 800, 704
OX, OY = 46, 112
PRETO = (22, 23, 23)
PAPEL = (246, 243, 232)
BRANCO = (255, 253, 245)
VERMELHO = (211, 38, 37)
AZUL = (27, 65, 151)
AMARELO = (249, 204, 35)
CINZA = (216, 212, 199)

# Matrizes quadradas conservam um pivô estável durante as rotações.
FORMAS = {
    'I': ('....', 'IIII', '....', '....'),
    'O': ('OO', 'OO'),
    'T': ('.T.', 'TTT', '...'),
    'S': ('.SS', 'SS.', '...'),
    'Z': ('ZZ.', '.ZZ', '...'),
    'J': ('J..', 'JJJ', '...'),
    'L': ('..L', 'LLL', '...'),
}
CORES = {'I': AZUL, 'O': AMARELO, 'T': VERMELHO,
         'S': AMARELO, 'Z': VERMELHO, 'J': AZUL, 'L': VERMELHO}


@dataclass
class Peca:
    tipo: str
    matriz: tuple
    x: int
    y: int = 0

    def blocos(self, matriz=None, x=None, y=None):
        """Converte coordenadas locais da peça para coordenadas do tabuleiro."""
        matriz = self.matriz if matriz is None else matriz
        x = self.x if x is None else x
        y = self.y if y is None else y
        return [(x + c, y + l) for l, linha in enumerate(matriz)
                for c, valor in enumerate(linha) if valor != '.']


class Jogo:
    """Modelo independente do Pygame: tabuleiro, colisões e pontuação."""

    def __init__(self, semente=None):
        self.aleatorio = random.Random(semente)
        self.reiniciar()

    def reiniciar(self):
        self.tabuleiro = [[None] * COLUNAS for _ in range(LINHAS)]
        self.saco = []
        self.fila = [self.sortear() for _ in range(3)]
        self.pontos = self.linhas = 0
        self.fim = self.pausado = False
        self.tempo_queda = self.tempo_chao = 0.0
        self.ajustes = 0
        self.mensagem = 'Encontre o ritmo. Componha o espaço.'
        self.nova_peca()

    @property
    def nivel(self):
        return 1 + self.linhas // 10

    @property
    def intervalo(self):
        return max(0.075, 0.8 * 0.82 ** (self.nivel - 1))

    def sortear(self):
        # Cada saco contém as sete peças uma vez, em ordem aleatória.
        if not self.saco:
            self.saco = list(FORMAS)
            self.aleatorio.shuffle(self.saco)
        return self.saco.pop()

    def nova_peca(self):
        tipo = self.fila.pop(0)
        self.fila.append(self.sortear())
        matriz = FORMAS[tipo]
        self.peca = Peca(tipo, matriz, (COLUNAS - len(matriz)) // 2)
        self.tempo_queda = self.tempo_chao = 0.0
        self.ajustes = 0
        if not self.cabe():
            self.fim = True

    def cabe(self, matriz=None, x=None, y=None):
        for c, l in self.peca.blocos(matriz, x, y):
            if c < 0 or c >= COLUNAS or l >= LINHAS:
                return False
            if l >= 0 and self.tabuleiro[l][c] is not None:
                return False
        return True

    def mover(self, dx, dy, manual=False):
        if self.fim or self.pausado:
            return False
        p = self.peca
        no_chao = not self.cabe(y=p.y + 1)
        if not self.cabe(x=p.x + dx, y=p.y + dy):
            return False
        p.x += dx
        p.y += dy
        if manual and dy > 0:
            self.pontos += dy
        if dx and no_chao and self.ajustes < 15:
            self.tempo_chao = 0
            self.ajustes += 1
        return True

    def girar(self, horario=True):
        if self.fim or self.pausado or self.peca.tipo == 'O':
            return False
        p = self.peca
        m = p.matriz
        nova = tuple(''.join(l) for l in zip(*m[::-1]))
        if not horario:
            nova = tuple(''.join(l) for l in zip(*m))[::-1]
        # Ajustes simples junto às paredes e ao chão (não é o SRS oficial).
        no_chao = not self.cabe(y=p.y + 1)
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0),
                       (0, -1), (-1, -1), (1, -1), (0, -2)):
            if self.cabe(nova, p.x + dx, p.y + dy):
                p.matriz, p.x, p.y = nova, p.x + dx, p.y + dy
                if no_chao and self.ajustes < 15:
                    self.tempo_chao = 0
                    self.ajustes += 1
                return True
        return False

    def destino(self):
        y = self.peca.y
        while self.cabe(y=y + 1):
            y += 1
        return y

    def soltar(self):
        if self.fim or self.pausado:
            return
        destino = self.destino()
        self.pontos += 2 * (destino - self.peca.y)
        self.peca.y = destino
        self.fixar()

    def fixar(self):
        blocos = self.peca.blocos()
        if any(l < 0 for _, l in blocos):
            self.fim = True
            return
        for c, l in blocos:
            self.tabuleiro[l][c] = self.peca.tipo
        restantes = [l for l in self.tabuleiro if any(v is None for v in l)]
        quantidade = LINHAS - len(restantes)
        if quantidade:
            self.pontos += (0, 100, 300, 500, 800)[quantidade] * self.nivel
            self.linhas += quantidade
            self.tabuleiro = [[None] * COLUNAS for _ in range(quantidade)] + restantes
            self.mensagem = ('COMPOSIÇÃO PERFEITA!  +4 linhas' if quantidade == 4
                             else f'Boa composição!  +{quantidade} linha(s)')
        self.nova_peca()

    def atualizar(self, dt, descendo=False):
        if self.fim or self.pausado:
            return
        self.tempo_queda += dt
        intervalo = min(self.intervalo, 0.035) if descendo else self.intervalo
        while self.tempo_queda >= intervalo:
            self.tempo_queda -= intervalo
            if not self.mover(0, 1, manual=descendo):
                self.tempo_queda = 0
                break
        if not self.cabe(y=self.peca.y + 1):
            self.tempo_chao += dt
            if self.tempo_chao >= 0.45:
                self.fixar()
        else:
            self.tempo_chao = 0


class Interface:
    def __init__(self, pygame):
        self.pg = pygame
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
        pygame.display.set_caption('Tetris Mondrian | composição em movimento')
        self.quadro = pygame.Surface((LARGURA, ALTURA))
        self.fontes = {n: pygame.font.SysFont('Arial', n, bold=True)
                       for n in (14, 16, 18, 24, 36, 42)}

    def texto(self, texto, x, y, tamanho=18, cor=PRETO):
        self.quadro.blit(self.fontes[tamanho].render(texto, True, cor), (x, y))

    def caixa(self, rect, cor, borda=4):
        self.pg.draw.rect(self.quadro, cor, rect)
        self.pg.draw.rect(self.quadro, PRETO, rect, borda)

    def bloco(self, x, y, cor, tamanho=CELULA, fantasma=False):
        rect = self.pg.Rect(x, y, tamanho, tamanho)
        if fantasma:
            self.pg.draw.rect(self.quadro, (153, 150, 137), rect.inflate(-6, -6), 2)
        else:
            self.caixa(rect, cor, 2)

    def desenhar(self, jogo):
        q = self.quadro
        q.fill(PAPEL)
        self.caixa((0, 0, 800, 88), BRANCO)
        self.caixa((0, 0, 22, 88), VERMELHO)
        self.texto('TETRIS', 43, 8, 42)
        self.texto('MONDRIAN', 216, 24, 24)
        self.texto('COMPOSIÇÃO EM MOVIMENTO', 46, 60, 14)
        self.caixa((640, 0, 160, 88), AZUL)
        self.caixa((596, 0, 44, 88), AMARELO)
        self.caixa((OX - 5, OY - 5, 290, 570), PRETO)
        for l in range(LINHAS):
            for c in range(COLUNAS):
                valor = jogo.tabuleiro[l][c]
                rect = (OX + c * CELULA, OY + l * CELULA, CELULA, CELULA)
                self.pg.draw.rect(q, BRANCO, rect)
                self.pg.draw.rect(q, CINZA, rect, 1)
                if valor:
                    self.bloco(rect[0], rect[1], CORES[valor])
        if not jogo.fim:
            for c, l in jogo.peca.blocos(y=jogo.destino()):
                if l >= 0:
                    self.bloco(OX + c * CELULA, OY + l * CELULA, CINZA, fantasma=True)
            for c, l in jogo.peca.blocos():
                if l >= 0:
                    self.bloco(OX + c * CELULA, OY + l * CELULA, CORES[jogo.peca.tipo])
        self.caixa((359, 108, 395, 126), BRANCO)
        self.texto('PONTUAÇÃO', 379, 122, 14)
        self.texto(f'{jogo.pontos:06d}', 379, 145, 36)
        self.texto(f'NÍVEL {jogo.nivel:02d}    /    LINHAS {jogo.linhas:03d}', 379, 204, 16)
        self.caixa((359, 246, 395, 143), BRANCO)
        self.texto('PRÓXIMAS COMPOSIÇÕES', 379, 259, 14)
        for i, tipo in enumerate(jogo.fila):
            blocos = Peca(tipo, FORMAS[tipo], 0).blocos()
            minx = min(c for c, _ in blocos)
            miny = min(l for _, l in blocos)
            for c, l in blocos:
                self.bloco(382 + i * 119 + (c - minx) * 23,
                           309 + (l - miny) * 23, CORES[tipo], 23)
        self.caixa((359, 401, 395, 205), BRANCO)
        self.texto('CONTROLES', 379, 415, 14)
        comandos = ['ESQUERDA / DIREITA    mover', 'CIMA ou X    girar horário',
                    'Z    girar anti-horário', 'BAIXO    acelerar queda',
                    'ESPAÇO    queda imediata', 'P    pausa     R    reinício     ESC    sair']
        for i, linha in enumerate(comandos):
            self.texto(linha, 379, 443 + i * 24, 16)
        self.caixa((359, 618, 395, 59), AMARELO)
        self.texto(jogo.mensagem, 374, 637, 14)
        if jogo.pausado or jogo.fim:
            sombra = self.pg.Surface((280, 560), self.pg.SRCALPHA)
            sombra.fill((246, 243, 232, 230))
            q.blit(sombra, (OX, OY))
            self.caixa((56, 315, 260, 132), BRANCO)
            self.texto('FIM DE JOGO' if jogo.fim else 'PAUSA', 75, 338, 24)
            self.texto('R para recomeçar' if jogo.fim else 'P para continuar', 75, 388, 18)
        # Escala uniforme: redimensionar a janela não deforma os quadrados.
        w, h = self.tela.get_size()
        escala = min(w / LARGURA, h / ALTURA)
        tamanho = (max(1, int(LARGURA * escala)), max(1, int(ALTURA * escala)))
        self.tela.fill(PRETO)
        self.tela.blit(self.pg.transform.smoothscale(q, tamanho),
                       ((w - tamanho[0]) // 2, (h - tamanho[1]) // 2))
        self.pg.display.flip()


def main():
    ui, jogo = Interface(pygame), Jogo()
    relogio = pygame.time.Clock()
    direcao_anterior, repeticao = 0, 0.0
    rodando = True
    while rodando:
        dt = min(relogio.tick(60) / 1000, 0.1)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.WINDOWFOCUSLOST:
                jogo.pausado = True
            elif evento.type == pygame.KEYDOWN:
                tecla = evento.key
                if tecla == pygame.K_ESCAPE:
                    rodando = False
                elif tecla == pygame.K_r:
                    jogo.reiniciar()
                elif tecla == pygame.K_p and not jogo.fim:
                    jogo.pausado = not jogo.pausado
                elif tecla in (pygame.K_UP, pygame.K_x):
                    jogo.girar()
                elif tecla == pygame.K_z:
                    jogo.girar(False)
                elif tecla == pygame.K_SPACE:
                    jogo.soltar()
        teclas = pygame.key.get_pressed()
        direcao = int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT])
        if jogo.pausado or jogo.fim:
            direcao_anterior, repeticao = 0, 0
        else:
            if direcao != direcao_anterior:
                if direcao:
                    jogo.mover(direcao, 0)
                repeticao = 0.16
            elif direcao:
                repeticao -= dt
                while repeticao <= 0:
                    jogo.mover(direcao, 0)
                    repeticao += 0.055
            direcao_anterior = direcao
        jogo.atualizar(dt, teclas[pygame.K_DOWN])
        ui.desenhar(jogo)
    pygame.quit()
    return 0


if __name__ == '__main__':
    sys.exit(main())
