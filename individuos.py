# Parametros simulacao

import random
import math

QTD_MAX_INDIVIDUOS = 5000
QTD_INICIAL_INDIVIDUOS = 2000
IDADE_MAX = 85                  
INTERVALO_REPRODUCAO = 3
TAXA_MUTACAO = 0.080            
INTENSIDADE_MUTACAO = 30      
DISTANCIA_REPRODUCAO = 50
FATOR_SOBREVIVENCIA = 0.5

AMBIENTE_X_MAX = 1000
AMBIENTE_Y_MAX = 600
MAX_DISTANCIA_COR = 441.67

ENERGIA_MAXIMA = 500           
ENERGIA_INICIAL = 200
CUSTO_MOVIMENTO = 2           
CUSTO_REPRODUCAO = 50


class Cor():
    '''rgb(red, green, blue)'''
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

        
class Genes():
    '''
    Instruções de como as proteinas vão ser criadas
    >>> guardam as infos de como os individuos vão ser
    '''
    def __init__(self, x_pos:int, y_pos:int, cor:Cor):
        self.x = x_pos
        self.y = y_pos
        self.cor = cor  

    def __str__(self):
        return (f"Pos:({self.x},{self.y}) "
                f"Cor:({self.cor.r},{self.cor.g},{self.cor.b})")


class Individuo():
    
    _id_counter = 0
    
    def __init__(self,
                 gene: Genes,
                 idade:int,
                 qtdfilhos:int,
                 energia: int,
                 idade_maxima:int = IDADE_MAX,
                #  pai:Individuo,
                #  mae:Individuo,
                 ):
        self.id = Individuo._id_counter
        Individuo._id_counter += 1
        
        self.gene = gene
        self.idade = idade
        self.idade_maxima = idade_maxima       
        self.qtdfilhos = qtdfilhos
        self.energia = energia

    def __str__(self):
        return f"Individuo(Idade: {self.idade}, Energia: {self.energia} Gene: [{self.gene}])"
    
      
class Mutacao():
    '''
    na  hora que o descendente for criado, vai ter uma pequena chance do
    dele sofrer uma mutação, mas essa mutação vai somar pequenos valores aleatórios da cor e da posição  dele
    fazendo ele ser ligeramente diferente dos pais isso se chama, [seleção natural]
    
    >>> modifica os genens e cria variações
    '''
    
    def __init__(self, intensidade:int=INTENSIDADE_MUTACAO, taxa:float=TAXA_MUTACAO):
        self.taxa = taxa
        self.intensidade = intensidade
        
    def verificar_chance(self) -> bool:
        return random.random() < self.taxa
            
    def _aplicar_mutacao(self, gene_descendente: Genes) -> Genes:
        
        # posicao
        mudanca_x = random.randint(-self.intensidade, self.intensidade)
        mudanca_y = random.randint(-self.intensidade, self.intensidade)
        
        # cor
        
        intensidade_cor = self.intensidade * 2
        mudanca_r = random.randint(-intensidade_cor, intensidade_cor)
        mudanca_g = random.randint(-intensidade_cor, intensidade_cor)
        mudanca_b = random.randint(-intensidade_cor, intensidade_cor)
                                                
        gene_descendente.x += mudanca_x
        gene_descendente.y += mudanca_y
        gene_descendente.cor.r += mudanca_r
        gene_descendente.cor.g += mudanca_g
        gene_descendente.cor.b += mudanca_b
                                                      
        gene_descendente.x = max(0, min(gene_descendente.x, AMBIENTE_X_MAX))
        gene_descendente.y = max(0, min(gene_descendente.y, AMBIENTE_Y_MAX))
        
        gene_descendente.cor.r = max(0, min(gene_descendente.cor.r, 255))
        gene_descendente.cor.g = max(0, min(gene_descendente.cor.g, 255))
        gene_descendente.cor.b = max(0, min(gene_descendente.cor.b, 255))

        return gene_descendente

                                                
        
    def mutar(self, gene_descendente: Genes) -> Genes:

        if self.verificar_chance():
            # print(f'-> Individuo sofreu uma mutação genética!')
            gene_mutado = self._aplicar_mutacao(gene_descendente)
            return gene_mutado
        else:
            return gene_descendente    


class ReproducaoSexuada():
    '''
    >>> perpetua as informações contidas nos genes
    '''
    def __init__(self, pai:Individuo, mae:Individuo):
        self.pai_gene = pai
        self.mae_gene = mae
    
    def reproduzir(self) -> Genes:
        pai_gene = self.pai_gene.gene
        mae_gene = self.mae_gene.gene
        filho_gene = None

        filho_x = random.choice([pai_gene.x, mae_gene.x])
        filho_y = random.choice([pai_gene.y, mae_gene.y])
        filho_r = random.choice([pai_gene.cor.r, mae_gene.cor.r])
        filho_g = random.choice([pai_gene.cor.g, mae_gene.cor.g])
        filho_b = random.choice([pai_gene.cor.b, mae_gene.cor.b])
    
        filho_gene_base = Genes(x_pos=filho_x, y_pos=filho_y, cor=Cor(filho_r, filho_g, filho_b))
        processo_mutacao = Mutacao()
        filho = processo_mutacao.mutar(filho_gene_base)
        
        return filho
  
     
    def __str__(self):
        return (f"PAI:({self.pai_gene}) "
                f"MAE:({self.mae_gene})")

   
class SelecaoNatural():
    '''
    >>> Filtra as melhores variações
    e direciona as características
    
    
    a cada iteração a o indivíduo tem uma chance de morrer, e a chance vai ser proporcional a diferenca da cor dele
    com a cor do ambiente que ele ta.
    
    
    distancia euclidiana
    '''    
    def __init__(self, cor_alvo: Cor, fator_de_pressao: float = FATOR_SOBREVIVENCIA):
        self.cor_alvo = cor_alvo
        self.fator_de_pressao = fator_de_pressao
    
    
    def _calcular_distancia_das_cores(self, cor1: Cor, cor2: Cor) -> float:
        '''Calcula a distancia euclidiana entre duas cores no espaco RGB'''
        
        delta_r = (cor1.r - cor2.r) ** 2
        delta_g = (cor1.g - cor2.g) ** 2
        delta_b = (cor1.b - cor2.b) ** 2
        
        return math.sqrt(delta_r + delta_g + delta_b)
        
        
    def _calcular_probabilidade_morte(self, distancia: float) -> float:
        ''' converte a distancia de cor em uma probabilidade de morte (0.0 a 1.0)'''
        
        probabilidade_base = distancia / MAX_DISTANCIA_COR
        
        probabilidade_ajustada = probabilidade_base * self.fator_de_pressao
    
        return max(0.0, min(1.0, probabilidade_ajustada))


    def aplicar_selecao(self, populacao: list[Individuo]) -> list[Individuo]:
        '''Filtra populacao, retornando uma nova lista apenas com os sobreviventes.'''
        
        sobreviventes = []
        
        for individuo in populacao:
            distancia = self._calcular_distancia_das_cores(individuo.gene.cor, self.cor_alvo)
            probabilidade_morte = self._calcular_probabilidade_morte(distancia)
            
            if random.random() > probabilidade_morte:
                sobreviventes.append(individuo)
                
        return sobreviventes
    
        

  
if __name__ == '__main__':
    pai_alguem = Individuo(gene=Genes(50, 100, cor=Cor(52, 201, 193)), idade=25, idade_maxima= 40, qtdfilhos=0)
    mae_alguem = Individuo(gene=Genes(200, 150, cor=Cor(217, 105, 31)), idade=18, idade_maxima= 35, qtdfilhos=1)

    processo_reprodutivo = ReproducaoSexuada(pai=pai_alguem, mae=mae_alguem)
    gene_filho = processo_reprodutivo.reproduzir()

    filho = Individuo(gene=gene_filho, idade=0, qtdfilhos=0)

    # print(f'Pai: {pai_alguem}')
    # print(f'Mae: {mae_alguem}')

