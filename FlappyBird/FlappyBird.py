import pygame
import os
import random
import neat

# esse github vai me ajudar a colocar uma linha
# https://github.com/bapiraj/flappy-bird-ai/blob/master/flappy.py


ai_jogando = True
geracao = 0
qtde = []
TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGEM_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('comicsans', 30)

class Passaros:
    IMGS = IMAGEM_PASSARO
    # Animação de Rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def pular(self):
        self.velocidade = -8 #mudei 20:43 06/09/2021
        self.tempo = 0
        self.altura = self.y

    def mover(self):

        # define o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 5 #original 2

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # Definir qual a imagem que será usada.

        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO * 4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # se o passaro estiver caindo:

        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        posicao_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=posicao_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)
        self.rect_passaro = pygame.Rect(self.x, self.y, imagem_rotacionada.get_width(), imagem_rotacionada.get_height())
        pygame.draw.rect(tela, self.color, (self.rect_passaro.x, self.rect_passaro.y,
                                            self.rect_passaro.width, self.rect_passaro.height), 2)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)

class Canos:
    DISTANCIA = 175
    VELOCIDADE_CANO = 20

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.posicao_topo = 0
        self.posicao_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):

        self.x -= self.VELOCIDADE_CANO

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

        self.rect_base = pygame.Rect(self.x, self.pos_base, self.CANO_BASE.get_width(),self.CANO_BASE.get_height())
        pygame.draw.rect(tela, self.color, (self.rect_base.x, self.rect_base.y, self.rect_base.width, self.rect_base.height), 5)

        self.rect_topo = pygame.Rect(self.x, self.pos_topo, self.CANO_BASE.get_width(),self.CANO_TOPO.get_height())
        pygame.draw.rect(tela, self.color, (self.rect_topo.x, self.rect_topo.y, self.rect_topo.width, self.rect_topo.height), 5)


    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE_CHAO = 5
    LARGURA_CHAO = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA_CHAO

    def mover(self):
        self.x1 -= self.VELOCIDADE_CHAO
        self.x2 -= self.VELOCIDADE_CHAO

        if self.x1 + self.LARGURA_CHAO < 0:
            self.x1 = self.x2 + self.LARGURA_CHAO
        if self.x2 + self.LARGURA_CHAO < 0:
            self.x2 = self.x1 + self.LARGURA_CHAO

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, Passaros, Canos, Chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in Passaros:
        passaro.desenhar(tela)
        pass
    for cano in Canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

    if ai_jogando:
        texto = FONTE_PONTOS.render(f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto, (10, 10))

        texto = FONTE_PONTOS.render(f"Qtd.: {qtde}", 1, (255, 255, 255))
        tela.blit(texto, (10, 30))

        texto = FONTE_PONTOS.render(f"Velocidade.: {cano.VELOCIDADE_CANO}", 1, (255, 255, 255))
        tela.blit(texto, (10, 50))

    Chao.desenhar(tela)
    pygame.display.update()

def main(genomas, config):  # fitness function
    global geracao, lista_genomas, qtde, velocidade, cano
    geracao += 1
    velocidade = 0
    cano = []

    if ai_jogando:
        redes = []
        lista_genomas = []
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0  # pontuação pra rede neural. Pontuacao interna.
            lista_genomas.append(genoma)
            passaros.append(Passaros(230, 350))  # Cria o Passaro nessa posição

    else:
        passaros = [Passaros(230, 350)]
    chao = Chao(730)
    canos = [Canos(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()
    rodando = True
    qtde = len(passaros)

    while rodando:
        relogio.tick(30)

        # Iteração do Usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

        indice_cano = 0

        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > canos[0].x + (canos[0].CANO_TOPO.get_width()):
                indice_cano = 1

        else:
            rodando = False
            break
        # mover as coisas
        for i, passaro in enumerate(passaros):
            passaro.mover()
            # aumentar a fitness do passaro
            lista_genomas[i].fitness += 0.1
            output = redes[i].activate((passaro.y,
                                        abs(passaro.y - canos[indice_cano].altura),
                                        abs(passaro.y - canos[indice_cano].pos_base)))
            # -1 e 1 - > se o output for maior que > 0.5 entao o passaro pula
            if output[0] > 0.5:
                passaro.pular()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    qtde = len(passaros)
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)

                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()

            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Canos(800))
            for genoma in lista_genomas:
                genoma.fitness += 5

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                lista_genomas.pop(i)
                redes.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)


def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config
                                )
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())

    if ai_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)


if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)