import pygame
import pandas as pd
import random
from ambiente import Ambiente, Bioma, Cor, BRANCO, PRETO,  FonteDeRecurso
from individuos import (
    Genes, Individuo, ReproducaoSexuada, SelecaoNatural, 
    IDADE_MAX, QTD_INICIAL_INDIVIDUOS, AMBIENTE_X_MAX, AMBIENTE_Y_MAX,
    QTD_MAX_INDIVIDUOS, DISTANCIA_REPRODUCAO,
    
    ENERGIA_INICIAL, ENERGIA_MAXIMA, CUSTO_MOVIMENTO, CUSTO_REPRODUCAO
)

# --- PARAMETROS VISUALIZAÇÃO ---

LARGURA_TELA = 1000
ALTURA_TELA = 600
FPS = 18
RAIO_INDIVIDUO = 5


# --- PARAMETROS SIMULACAO ---
INTENSIDADE_MIGRACAO = 50       
NUMERO_DE_ANOS = 20000
IDADE_REPRODUTIVA = 10

QTD_FONTES_POR_BIOMA = 1
RAIO_FONTE_RECURSO = 80
INTENSIDADE_MOV_RECURSO = 5
INTENSIDADE_VARIACAO_COR = 0

class Camera:
    def __init__(self):
        self.zoom = min(LARGURA_TELA / AMBIENTE_X_MAX, ALTURA_TELA / AMBIENTE_Y_MAX)
        self.offset_x = 0
        self.offset_y = 0
        self.arrastando = False
        self.mouse_pos_inicial = (0, 0)
        
    def mundo_para_tela(self, x_mundo, y_mundo):
        '''converte coordenadas do mundo da simulacao para coordenadas da tela.'''
        
        x_tela = (x_mundo - self.offset_x) * self.zoom
        y_tela = (y_mundo - self.offset_y) * self.zoom
        return int(x_tela), int(y_tela)
    
    
    def raio_para_tela(self, raio_mundo):
        '''converte o raio de um objeto para o tamanho na tela -> considera o zoom '''
        return max(1, int(raio_mundo * self.zoom))
    
    def lidar_eventos(self, evento):
        '''processa os eventos do mouse para zoom e pan'''
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: # Botão esquerdo do mouse
                self.arrastando = True
                self.mouse_pos_inicial = evento.pos
            if evento.button == 4: # Scroll para cima (zoom in)
                self.zoom *= 1.1
            if evento.button == 5: # scroll para baixo (zoom out)
                self.zoom /= 1.1
                
        if evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1:
                self.arrastando = False
                
        if evento.type == pygame.MOUSEMOTION and self.arrastando:
            mouse_x_atual, mouse_y_atual = evento.pos
            mouse_x_inicial, mouse_y_inicial = self.mouse_pos_inicial
            
            # Ajusta o offset baseado no movimento do mouse e no zoo,
            self.offset_x -= (mouse_x_atual - mouse_x_inicial) / self.zoom
            self.offset_y -= (mouse_y_atual - mouse_y_inicial) / self.zoom
            
            self.mouse_pos_inicial = evento.pos
            
                
def cria_populacao_inicial(quantidade: int, ambiente: Ambiente) -> list[Individuo]:
    ''' Cria uma populacao inicial, diversificada e distribuída dentro de cada bioma.'''
    
    populacao = []
    qtd_por_bioma = quantidade // len(ambiente.biomas)

    for bioma in ambiente.biomas:
        limites = bioma.limites
        for _ in range(qtd_por_bioma):
            gene = Genes(
                x_pos= random.randint(limites['x_inicio'], limites['x_fim']),
                y_pos= random.randint(limites['y_inicio'], limites['y_fim']),
                cor=Cor(r=random.randint(0, 255), g=random.randint(0, 255), b=random.randint(0, 255))
            )
            
            individuo = Individuo(gene=gene, idade=random.randint(0, IDADE_MAX), qtdfilhos=0, energia=ENERGIA_INICIAL)
            populacao.append(individuo)
            
    return populacao
    

def pega_bioma_do_individuo(individuo: Individuo, ambiente: Ambiente) -> Bioma:
    x, y = individuo.gene.x, individuo.gene.y
    for bioma in ambiente.biomas:
        limites = bioma.limites
        if limites['x_inicio'] <= x <= limites['x_fim'] and limites['y_inicio'] <= y <= limites['y_fim']:
            return bioma
    return None


def mover_populacao(populacao: list[Individuo]):
    for individuo in populacao:
        mov_x = random.randint(-INTENSIDADE_MIGRACAO, INTENSIDADE_MIGRACAO)
        mov_y = random.randint(-INTENSIDADE_MIGRACAO, INTENSIDADE_MIGRACAO)
        
        individuo.gene.x += mov_x
        individuo.gene.y += mov_y
    
        individuo.gene.x = max(0, min(individuo.gene.x, AMBIENTE_X_MAX))
        individuo.gene.y = max(0, min(individuo.gene.y, AMBIENTE_Y_MAX))
        
        individuo.energia -= CUSTO_MOVIMENTO


def variar_cores_biomas(ambiente: Ambiente, intensidade: int):
    """Altera sutilmente a cor de cada bioma a cada ano."""
    for bioma in ambiente.biomas:
        dr = random.randint(-intensidade, intensidade)
        dg = random.randint(-intensidade, intensidade)
        db = random.randint(-intensidade, intensidade)

        bioma.cor.r = max(0, min(255, bioma.cor.r + dr))
        bioma.cor.g = max(0, min(255, bioma.cor.g + dg))
        bioma.cor.b = max(0, min(255, bioma.cor.b + db))

# --- FUNÇÕES DE DENSENHO ---

def desenhar_fontes_recurso(tela, ambiente: Ambiente, camera: Camera):
    for bioma in ambiente.biomas:
        for f in bioma.fontes_de_recurso:
            pos_tela = camera.mundo_para_tela(f.x, f.y)
            raio_tela = camera.raio_para_tela(f.raio)
            
            # Se o raio for muito pequeno, não desenha para evitar poluição visual
            if raio_tela < 2:
                continue

            # 1. Define o raio da borda e o tamanho da superfície com base nela
            raio_borda = raio_tela + 1
            tamanho_surface = raio_borda * 2
            
            # 2. Cria a superfície com o tamanho correto
            surface = pygame.Surface((tamanho_surface, tamanho_surface), pygame.SRCALPHA)
            
            # O centro da superfície agora é (raio_borda, raio_borda)
            centro_surface = (raio_borda, raio_borda)

            # 3. Desenha a borda PRETA e PREENCHIDA no centro da superfície
            pygame.draw.circle(surface, PRETO, centro_surface, raio_borda)

            # 4. Desenha o círculo verde transparente por cima, também no centro
            pygame.draw.circle(surface, (200, 255, 200, 60), centro_surface, raio_tela)
            
            # 5. Posiciona a superfície na tela, ajustando pelo raio da borda
            pos_blit = (pos_tela[0] - raio_borda, pos_tela[1] - raio_borda)
            tela.blit(surface, pos_blit)

def desenhar_ambiente(tela, ambiente: Ambiente, camera: Camera):
    for bioma in ambiente.biomas:
        lim = bioma.limites
        cor_bioma = (bioma.cor.r, bioma.cor.g, bioma.cor.b)
        
        x_tela, y_tela = camera.mundo_para_tela(lim['x_inicio'], lim['y_inicio'])
        x_fim_tela, y_fim_tela = camera.mundo_para_tela(lim['x_fim'], lim['y_fim'])
        
        largura_tela = x_fim_tela - x_tela
        altura_tela = y_fim_tela - y_tela
        
        retangulo = pygame.Rect(x_tela, y_tela, largura_tela, altura_tela)
        pygame.draw.rect(tela, cor_bioma, retangulo)
        
def desenhar_populacao(tela, populacao: list[Individuo], camera: Camera):
    for individuo in populacao:
        
        pos_tela = camera.mundo_para_tela(individuo.gene.x, individuo.gene.y)
        raio_tela = camera.raio_para_tela(RAIO_INDIVIDUO)
        
        cor = (individuo.gene.cor.r, individuo.gene.cor.g, individuo.gene.cor.b)
        
        pygame.draw.circle(tela, PRETO, pos_tela, raio_tela + 1, 1)
        pygame.draw.circle(tela, cor, pos_tela, raio_tela)
        
def desenhar_info(tela, ano:int, pop_total: int, fonte):
    texto_ano = fonte.render(f"Ano: {ano}", True, BRANCO)
    texto_pop = fonte.render(f"População: {pop_total}", True, BRANCO)
    tela.blit(texto_ano, (10, 10))
    tela.blit(texto_pop, (10, 35))
    

# --- FUNCAO PRINCIPAL ---
def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption('Simulação de Evolução Genética [Scroll=Zoom, Arrastar=Mover]', '👥')
    clock = pygame.time.Clock()
    fonte = pygame.font.Font(None, 30)
    
    camera = Camera()
    
    maritimo  = Bioma('marítimo',  0.10, Cor(28, 107, 160), energia_fornecida=50)
    polar     = Bioma('polar',     0.5, Cor(102, 183, 255), energia_fornecida=200)
    floresta  = Bioma('floresta',  0.20, Cor(34, 139, 34), energia_fornecida=40)
    desertico = Bioma('desértico', 0.20, Cor(237, 201, 175), energia_fornecida=90)
    savanna   = Bioma('savanna',   0.5, Cor(189, 183, 107), energia_fornecida=200)
    pantano   = Bioma('pântano',   0.5, Cor(47, 79, 79), energia_fornecida=200)
    montanha  = Bioma('montanha',  0.10, Cor(139, 137, 137), energia_fornecida=20)
    tundra    = Bioma('tundra',    0.5, Cor(176, 224, 230), energia_fornecida=200)
    planicie  = Bioma('planície',  0.10, Cor(144, 238, 144), energia_fornecida=20)
    vulcanico = Bioma('vulcânico', 0.10, Cor(178, 34, 34), energia_fornecida=90)

    ambiente = Ambiente(
        AMBIENTE_X_MAX, AMBIENTE_Y_MAX,
        [
            maritimo, floresta, desertico, polar,
            savanna, pantano, montanha, tundra, planicie, vulcanico
        ]
    )
    
    ambiente._calcular_limites_biomas()
    
    for bioma in ambiente.biomas:
        for _ in range(QTD_FONTES_POR_BIOMA):
            lim = bioma.limites
            x_rand = random.randint(lim['x_inicio'], lim['x_fim'])
            y_rand = random.randint(lim['y_inicio'], lim['y_fim'])
            fonte_obj = FonteDeRecurso(x_rand, y_rand, RAIO_FONTE_RECURSO, bioma.energia_fornecida)
            bioma.fontes_de_recurso.append(fonte_obj)
    
    populacao = cria_populacao_inicial(QTD_INICIAL_INDIVIDUOS, ambiente)
    
    rodando = True
    ano_atual = 0
    
    dados_individuais_log = [] 
    
    while rodando and ano_atual < NUMERO_DE_ANOS:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            camera.lidar_eventos(evento)
                
        if not populacao:
            print('>>> A POPULACAO FOI EXTINTA! <<<')
            rodando = False
            continue
        
        # --- LÓGICA DA SIMULAÇÃO (1 ANO) ---
        
        for bioma in ambiente.biomas:
            for fonte_obj in bioma.fontes_de_recurso:
                fonte_obj.mover(bioma.limites, INTENSIDADE_MOV_RECURSO)
        variar_cores_biomas(ambiente, INTENSIDADE_VARIACAO_COR)
        
        # 1. Envelhecer e alimentar a população
        for individuo in populacao: 
            individuo.idade += 1
            for bioma in ambiente.biomas:
                for fonte_obj in bioma.fontes_de_recurso:
                    dist_sq = (individuo.gene.x - fonte_obj.x)**2 + (individuo.gene.y - fonte_obj.y)**2
                    if dist_sq <= fonte_obj.raio**2:
                        individuo.energia += fonte_obj.energia_fornecida
                        individuo.energia = min(individuo.energia, ENERGIA_MAXIMA)
                        break
                else:
                    continue
                break
                
        # 2. Mover a população
        mover_populacao(populacao)
        
        # --- ESTRUTURA LÓGICA CORRIGIDA ---

        # 3. Seleção Natural (por cor de camuflagem)
        populacao_por_bioma = {bioma: [] for bioma in ambiente.biomas}
        for individuo in populacao:
            bioma_do_individuo = pega_bioma_do_individuo(individuo, ambiente)
            if bioma_do_individuo:
                populacao_por_bioma[bioma_do_individuo].append(individuo)
        
        sobreviventes_gerais = []
        for bioma, individuos_no_bioma in populacao_por_bioma.items():
            if individuos_no_bioma:
                selecao = SelecaoNatural(cor_alvo=bioma.cor)
                sobreviventes_do_bioma = selecao.aplicar_selecao(individuos_no_bioma)
                sobreviventes_gerais.extend(sobreviventes_do_bioma)
                
        populacao = sobreviventes_gerais
        
        # 4. Reprodução
        novos_descendentes = []
        aptos = [
            ind for ind in populacao
            if ind.idade >= IDADE_REPRODUTIVA and ind.energia >= CUSTO_REPRODUCAO
        ]
        random.shuffle(aptos)
        
        ja_reproduziu = set()
        for individuo_a in aptos:
            if individuo_a in ja_reproduziu:
                continue

            for individuo_b in aptos:
                if individuo_a is not individuo_b and individuo_b not in ja_reproduziu:
                    dist_x = individuo_a.gene.x - individuo_b.gene.x
                    dist_y = individuo_a.gene.y - individuo_b.gene.y
                    
                    if (dist_x**2 + dist_y**2) <= DISTANCIA_REPRODUCAO**2:
                        reproducao = ReproducaoSexuada(pai=individuo_a, mae=individuo_b)
                        novo_gene = reproducao.reproduzir()
                        novo_filho = Individuo(gene=novo_gene, idade=0, qtdfilhos=0, energia=ENERGIA_INICIAL)
                        novos_descendentes.append(novo_filho)
                        
                        individuo_a.energia -= CUSTO_REPRODUCAO
                        individuo_b.energia -= CUSTO_REPRODUCAO
                        
                        ja_reproduziu.add(individuo_a)
                        ja_reproduziu.add(individuo_b)
                        break
        
        populacao.extend(novos_descendentes)
        
        # 5. Morte por idade/fome e Controle Populacional
        populacao = [ind for ind in populacao if ind.idade < IDADE_MAX and ind.energia > 0]

        # 5.1 Controle de capacidade por bioma
        populacao_por_bioma = {bioma: [] for bioma in ambiente.biomas}
        for individuo in populacao:
            bioma_do_individuo = pega_bioma_do_individuo(individuo, ambiente)
            if bioma_do_individuo:
                populacao_por_bioma[bioma_do_individuo].append(individuo)

        populacao_controlada = []
        for bioma, individuos_no_bioma in populacao_por_bioma.items():
            if len(individuos_no_bioma) > bioma.capacidade_maxima:
                sobreviventes_do_bioma = random.sample(individuos_no_bioma, bioma.capacidade_maxima)
                populacao_controlada.extend(sobreviventes_do_bioma)
            else:
                populacao_controlada.extend(individuos_no_bioma)
        
        populacao = populacao_controlada

        # 5.2 Controle de capacidade global
        if len(populacao) > QTD_MAX_INDIVIDUOS:
            populacao = random.sample(populacao, QTD_MAX_INDIVIDUOS)
                
        print(f'Ano {ano_atual+1}: População = {len(populacao)}')
        
        for individuo in populacao:
            bioma_atual = pega_bioma_do_individuo(individuo, ambiente)
            nome_bioma = bioma_atual.nome if bioma_atual else 'Nenhum'
            
            registro_individuo = {
                'Ano': ano_atual + 1,
                'ID_Individuo': individuo.id,
                'Idade': individuo.idade,
                'Energia': individuo.energia,
                'X_Pos': individuo.gene.x,
                'Y_Pos': individuo.gene.y,
                'Cor_R': individuo.gene.cor.r,
                'Cor_G': individuo.gene.cor.g,
                'Cor_B': individuo.gene.cor.b,
                'Bioma': nome_bioma,
            }
            dados_individuais_log.append(registro_individuo)

        # --- FASE DE DESENHO ----
        tela.fill(PRETO)
        desenhar_ambiente(tela, ambiente, camera)
        desenhar_fontes_recurso(tela, ambiente, camera)
        desenhar_populacao(tela, populacao, camera)
        desenhar_info(tela, ano_atual+1, len(populacao), fonte)
        
        pygame.display.flip()
        
        # --- CONTROLE DE TEMPO ---
        clock.tick(FPS)
        ano_atual += 1
    
    print("\n--- SALVANDO DADOS GRANULARES DA SIMULAÇÃO ---")
    if dados_individuais_log:
        df_simulacao = pd.DataFrame(dados_individuais_log)
        
        # Salva em CSV, que é muito mais eficiente para arquivos grandes
        nome_arquivo_csv = "dados_individuais_simulacao.csv"
        df_simulacao.to_csv(nome_arquivo_csv, index=False)
        print(f"Dados salvos com sucesso em '{nome_arquivo_csv}'")
    else:
        print("Nenhum dado foi gerado para salvar.")
    
    print("\n--- SIMULAÇÃO FINALIZADA ---")
    print("A janela final está sendo exibida. Pressione qualquer tecla para fechar.")
    
    aguardando_fechar = True
    while aguardando_fechar:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                aguardando_fechar = False
            if event.type == pygame.KEYDOWN:
                aguardando_fechar = False

        texto_final = fonte.render("Pressione qualquer tecla para sair", True, BRANCO)
        rect_final = texto_final.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2))
        pygame.draw.rect(tela, PRETO, rect_final.inflate(20, 20))
        tela.blit(texto_final, rect_final)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()