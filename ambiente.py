import random
from individuos import Cor, AMBIENTE_X_MAX, AMBIENTE_Y_MAX, QTD_MAX_INDIVIDUOS

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

class Bioma():
    def __init__(self, nome: str, proporcao: float, cor: Cor, energia_fornecida: int):
        self.nome = nome
        self.cor = cor
        self.proporcao = max(0.0, min(1.0, proporcao))
        self.energia_fornecida = energia_fornecida
        self.limites = None
        self.fontes_de_recurso = []
        self.capacidade_maxima = 0
        
class Ambiente():
    def __init__(self, tamanho_x:int, tamanho_y:int ,biomas:list[Bioma]):
        self.tamanho_x = tamanho_x
        self.tamanho_y = tamanho_y
        self.biomas = biomas

            
    def _calcular_limites_biomas(self):
        '''
        Calcula os limites de cada bioma com base na sua proporção,

        '''
        
        # Usar uma cópia da lista para não modificar a original
        biomas_para_alocar = sorted(self.biomas, key=lambda b: b.proporcao, reverse=True)
        
        # Define a área retangular inicial que será dividida
        espaco_restante = {
            'x': 0, 
            'y': 0, 
            'largura': self.tamanho_x, 
            'altura': self.tamanho_y
        }
        area_total_ambiente = self.tamanho_x * self.tamanho_y
        
        while biomas_para_alocar:
            soma_proporcoes_restantes = sum(b.proporcao for b in biomas_para_alocar)
            
            # Pega o primeiro bioma da lista para alocar no espaço restante
            bioma_atual = biomas_para_alocar.pop(0)
            
            # Se for o último bioma, ele ocupa todo o espaço que sobrou para evitar vãos
            if not biomas_para_alocar:
                bioma_atual.limites = {
                    'x_inicio': espaco_restante['x'],
                    'x_fim': espaco_restante['x'] + espaco_restante['largura'] - 1,
                    'y_inicio': espaco_restante['y'],
                    'y_fim': espaco_restante['y'] + espaco_restante['altura'] - 1,
                }
            else:

                # Decide se corta na vertical ou na horizontal
                corte_vertical = espaco_restante['largura'] > espaco_restante['altura']
                
                fracao_espaco = bioma_atual.proporcao / soma_proporcoes_restantes

                if corte_vertical:
                    largura_fatia = int(fracao_espaco * espaco_restante['largura'])
                    bioma_atual.limites = {
                        'x_inicio': espaco_restante['x'],
                        'x_fim': espaco_restante['x'] + largura_fatia - 1,
                        'y_inicio': espaco_restante['y'],
                        'y_fim': espaco_restante['y'] + espaco_restante['altura'] - 1,
                    }
                    # Atualiza o espaço restante para a próxima iteração
                    espaco_restante['x'] += largura_fatia
                    espaco_restante['largura'] -= largura_fatia
                else: # Corte horizontal
                    altura_fatia = int(fracao_espaco * espaco_restante['altura'])
                    bioma_atual.limites = {
                        'x_inicio': espaco_restante['x'],
                        'x_fim': espaco_restante['x'] + espaco_restante['largura'] - 1,
                        'y_inicio': espaco_restante['y'],
                        'y_fim': espaco_restante['y'] + altura_fatia - 1,
                    }
                    # Atualiza o espaço restante para a próxima iteração
                    espaco_restante['y'] += altura_fatia
                    espaco_restante['altura'] -= altura_fatia

            largura_bioma = bioma_atual.limites['x_fim'] - bioma_atual.limites['x_inicio']
            altura_bioma = bioma_atual.limites['y_fim'] - bioma_atual.limites['y_inicio']
            area_bioma = largura_bioma * altura_bioma
            
            proporcao_area = area_bioma / area_total_ambiente
            bioma_atual.capacidade_maxima = int(proporcao_area * QTD_MAX_INDIVIDUOS)

    def mostrar(self):
        print(f'Ambiente com tamanho [{self.tamanho_x}, {self.tamanho_y}]')
        print('-' * 40)
        # Passo 5: Usar self.biomas em vez da variável global
        if not self.biomas or self.biomas[0].limites is None:
            print("Limites dos biomas ainda não foram calculados. Chame _calcular_limites_biomas() primeiro.")
            return
            
        for bioma in self.biomas:
            # Passo 6: Corrigido de 'limite' para 'limites' e impressão mais clara
            print(f"Bioma: {bioma.nome:<10} | Proporção: {bioma.proporcao * 100:.1f}% | "
                  f"Capacidade: {bioma.capacidade_maxima:<5} | Limites: {bioma.limites}")


class FonteDeRecurso:
    def __init__(self, x: int, y: int, raio, energia_fornecida: int):
        self.x = x
        self.y = y
        self.raio = raio
        self.energia_fornecida = energia_fornecida
        
    def mover(self, limites_bioma: dict, intensidade_movimento: int):
        '''
        mova a fonte de recurso aleatoriamente dentro dos limites de seu bioma
        ''' 

        mov_x = random.randint(-intensidade_movimento, intensidade_movimento)
        mov_y = random.randint(-intensidade_movimento, intensidade_movimento)
        
        self.x += mov_x
        self.y += mov_y
        
        self.x = max(limites_bioma['x_inicio'], min(self.x, limites_bioma['x_fim'])) 
        self.y = max(limites_bioma['y_inicio'], min(self.y, limites_bioma['y_fim'])) 
        

if __name__ == '__main__':
        

    maritimo = Bioma('maritmo',0.50, Cor(16, 49, 70), energia_fornecida=5)
    floresta = Bioma('floresta', 0.30, Cor(34, 139, 34), energia_fornecida=10)
    desertico = Bioma('desertico',0.10, Cor(193, 147, 107), energia_fornecida=2)
    polar = Bioma('polar',0.10, Cor(84, 91, 95), energia_fornecida=3)

    biomas = [maritimo, floresta, desertico, polar]

    ambiente = Ambiente(AMBIENTE_X_MAX, AMBIENTE_Y_MAX, biomas)  
    ambiente._calcular_limites_biomas()
    ambiente.mostrar()
    # print()