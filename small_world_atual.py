from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import List, Set, Dict
import matplotlib.pyplot as plt
import numpy as np

class Estado(Enum):
    DESINFORMADO = 0
    CIENTE = 1
    INTERESSADO = 2
    ABANDONOU = 3


@dataclass
class Individuo:
    estado: Estado = Estado.DESINFORMADO
    memoria_acumulada: int = 0
    tempo_no_estado: int = 0


def criar_rede_small_world(
    quantidade_individuos: int,
    grau_medio: int,
    probabilidade_religacao: float,
    gerador_aleatorio: Random
) -> List[Set[int]]:
    """
    Cria uma rede Small-World utilizando o modelo de Watts-Strogatz.

    quantidade_individuos -> quantidade de nós da rede
    grau_medio -> quantidade média de conexões por nó
    probabilidade_religacao -> probabilidade de religar uma aresta
    """

    if grau_medio % 2 != 0:
        raise ValueError("O grau médio deve ser par.")

    if grau_medio >= quantidade_individuos:
        raise ValueError(
            "O grau médio deve ser menor que a quantidade de indivíduos."
        )

    rede = [set() for _ in range(quantidade_individuos)]

    metade_grau = grau_medio // 2

    # Construção do anel regular
    for individuo in range(quantidade_individuos):

        for distancia in range(1, metade_grau + 1):

            vizinho = (individuo + distancia) % quantidade_individuos

            rede[individuo].add(vizinho)
            rede[vizinho].add(individuo)

    # Processo de rewiring (religação)
    for individuo in range(quantidade_individuos):

        for distancia in range(1, metade_grau + 1):

            vizinho = (individuo + distancia) % quantidade_individuos

            # evita processar a mesma aresta duas vezes
            if (
                individuo < vizinho
                and gerador_aleatorio.random() < probabilidade_religacao
            ):

                rede[individuo].discard(vizinho)
                rede[vizinho].discard(individuo)

                novo_vizinho = gerador_aleatorio.randrange(
                    quantidade_individuos
                )

                while (
                    novo_vizinho == individuo
                    or novo_vizinho in rede[individuo]
                ):
                    novo_vizinho = gerador_aleatorio.randrange(
                        quantidade_individuos
                    )

                rede[individuo].add(novo_vizinho)
                rede[novo_vizinho].add(individuo)

    return rede


def calcular_probabilidade_propagacao(
    quantidade_vizinhos_interessados: int,
    quantidade_vizinhos_abandonaram: int,
    quantidade_vizinhos: int,
    taxa_infeccao: float
) -> float:
    """
    Calcula a probabilidade de propagação da informação.
    """

    if quantidade_vizinhos == 0:
        return 0.0

    componente_infeccao = (
        1.0
        - (1.0 - taxa_infeccao) ** quantidade_vizinhos_interessados
    )

    efeito_manada_positivo = (
        1.0
        - pow(
            2.718281828,
            -(quantidade_vizinhos_interessados / quantidade_vizinhos)
        )
    )

    efeito_manada_negativo = (
        1.0
        - pow(
            2.718281828,
            -(quantidade_vizinhos_abandonaram / quantidade_vizinhos)
        )
    )

    efeito_manada = (
        (efeito_manada_positivo - efeito_manada_negativo)
        / (1.0 - 1.0 / 2.718281828)
    )

    probabilidade = (
        0.5 * componente_infeccao
        + 0.5 * efeito_manada
    )

    return max(0.0, min(1.0, probabilidade))


def calcular_atenuacao(
    tempo_no_estado: int,
    quantidade_vizinhos_interessados: int,
    quantidade_vizinhos: int
) -> float:
    """
    Calcula a atenuação da informação.
    """

    if quantidade_vizinhos == 0:
        return 0.0

    return (
        pow(2.718281828, -tempo_no_estado)
        * (quantidade_vizinhos_interessados / quantidade_vizinhos)
    )


def executar_passo_simulacao(
    rede: List[Set[int]],
    individuos: List[Individuo],
    taxa_infeccao: float,
    limite_memoria: int,
    limite_atenuacao: float,
    gerador_aleatorio: Random
) -> List[Individuo]:
    """
    Executa um passo da simulação.
    """

    proximos_individuos = [

        Individuo(
            estado=individuo.estado,
            memoria_acumulada=individuo.memoria_acumulada,
            tempo_no_estado=individuo.tempo_no_estado
        )

        for individuo in individuos
    ]

    for indice_individuo, individuo in enumerate(individuos):

        vizinhos = rede[indice_individuo]

        quantidade_vizinhos = len(vizinhos)

        quantidade_vizinhos_interessados = sum(
            1
            for vizinho in vizinhos
            if individuos[vizinho].estado == Estado.INTERESSADO
        )

        quantidade_vizinhos_abandonaram = sum(
            1
            for vizinho in vizinhos
            if individuos[vizinho].estado == Estado.ABANDONOU
        )

        # DESINFORMADO
        if individuo.estado == Estado.DESINFORMADO:

            if quantidade_vizinhos_interessados > 0:

                probabilidade = calcular_probabilidade_propagacao(
                    quantidade_vizinhos_interessados,
                    quantidade_vizinhos_abandonaram,
                    quantidade_vizinhos,
                    taxa_infeccao
                )

                if gerador_aleatorio.random() < probabilidade:

                    proximos_individuos[
                        indice_individuo
                    ].estado = Estado.INTERESSADO

                else:

                    proximos_individuos[
                        indice_individuo
                    ].estado = Estado.CIENTE

                proximos_individuos[
                    indice_individuo
                ].memoria_acumulada = 0

                proximos_individuos[
                    indice_individuo
                ].tempo_no_estado = 0

        # CIENTE
        elif individuo.estado == Estado.CIENTE:

            if quantidade_vizinhos_interessados > 0:

                proximos_individuos[
                    indice_individuo
                ].memoria_acumulada += 1

            else:

                proximos_individuos[
                    indice_individuo
                ].memoria_acumulada -= 1

            if (
                proximos_individuos[
                    indice_individuo
                ].memoria_acumulada >= limite_memoria
            ):

                proximos_individuos[
                    indice_individuo
                ].estado = Estado.INTERESSADO

                proximos_individuos[
                    indice_individuo
                ].tempo_no_estado = 0

            elif (
                proximos_individuos[
                    indice_individuo
                ].memoria_acumulada <= -limite_memoria
            ):

                proximos_individuos[
                    indice_individuo
                ].estado = Estado.ABANDONOU

        # INTERESSADO
        elif individuo.estado == Estado.INTERESSADO:

            valor_atenuacao = calcular_atenuacao(
                individuo.tempo_no_estado,
                quantidade_vizinhos_interessados,
                quantidade_vizinhos
            )

            if valor_atenuacao < limite_atenuacao:

                proximos_individuos[
                    indice_individuo
                ].estado = Estado.ABANDONOU

            else:

                proximos_individuos[
                    indice_individuo
                ].tempo_no_estado += 1

    return proximos_individuos


def contar_estados(
    individuos: List[Individuo]
) -> Dict[Estado, int]:

    contagem = {
        estado: 0
        for estado in Estado
    }

    for individuo in individuos:
        contagem[individuo.estado] += 1

    return contagem


def executar_simulacao(
    quantidade_individuos: int = 2500,
    grau_medio: int = 6,
    probabilidade_religacao: float = 0.1,
    quantidade_passos: int = 30,
    taxa_infeccao: float = 0.35,
    limite_memoria: int = 1,
    limite_atenuacao: float = 0.5,
    semente: int = 42,
    iniciais_interessados: int = 1 
):

    gerador_aleatorio = Random(semente)

    rede = criar_rede_small_world(
        quantidade_individuos,
        grau_medio,
        probabilidade_religacao,
        gerador_aleatorio
    )

    individuos = [
        Individuo()
        for _ in range(quantidade_individuos)
    ]

    # indivíduo inicial espalhando informação
    individuos[quantidade_individuos // 2].estado = Estado.INTERESSADO

    historico = []

    for tempo in range(quantidade_passos + 1):

        contagem = contar_estados(individuos)

        historico.append({
            "tempo": tempo,

            "desinformado":
                contagem[Estado.DESINFORMADO]
                / quantidade_individuos,

            "ciente":
                contagem[Estado.CIENTE]
                / quantidade_individuos,

            "interessado":
                contagem[Estado.INTERESSADO]
                / quantidade_individuos,

            "abandonou":
                contagem[Estado.ABANDONOU]
                / quantidade_individuos
        })

        if tempo < quantidade_passos:

            individuos = executar_passo_simulacao(
                rede=rede,
                individuos=individuos,
                taxa_infeccao=taxa_infeccao,
                limite_memoria=limite_memoria,
                limite_atenuacao=limite_atenuacao,
                gerador_aleatorio=gerador_aleatorio
            )

    return historico

def executar_simulacao_iniciais(
    quantidade_individuos: int = 2500,
    grau_medio: int = 6,
    probabilidade_religacao: float = 0.1,
    quantidade_passos: int = 30,
    taxa_infeccao: float = 0.35,
    limite_memoria: int = 1,
    limite_atenuacao: float = 0.5,
    semente: int = 42,
    iniciais_interessados: int = 1
):
    gerador_aleatorio = Random(semente)

    rede = criar_rede_small_world(
        quantidade_individuos,
        grau_medio,
        probabilidade_religacao,
        gerador_aleatorio
    )

    individuos = [Individuo() for _ in range(quantidade_individuos)]

    iniciais = gerador_aleatorio.sample(range(quantidade_individuos), iniciais_interessados)
    for j in range(iniciais_interessados):
        individuos[j].estado = Estado.INTERESSADO


    historico = []
    for tempo in range(quantidade_passos + 1):
        contagem = contar_estados(individuos)
        historico.append({
    		"tempo": tempo,
   		"desinformado": contagem[Estado.DESINFORMADO],
    		"ciente": contagem[Estado.CIENTE],
    		"interessado": contagem[Estado.INTERESSADO],
    		"abandonou": contagem[Estado.ABANDONOU]
})


        if tempo < quantidade_passos:
            individuos = executar_passo_simulacao(
                rede=rede,
                individuos=individuos,
                taxa_infeccao=taxa_infeccao,
                limite_memoria=limite_memoria,
                limite_atenuacao=limite_atenuacao,
                gerador_aleatorio=gerador_aleatorio
            )

    return historico



if __name__ == "__main__":

    historico = executar_simulacao(iniciais_interessados=1)

    print(
        "tempo,desinformado,ciente,interessado,abandonou"
    )

    for linha in historico:

        print(
            f"{linha['tempo']},"
            f"{linha['desinformado']:.4f},"
            f"{linha['ciente']:.4f},"
            f"{linha['interessado']:.4f},"
            f"{linha['abandonou']:.4f}"
        )
# Gráfico 1
# Definir diferentes taxas de infecção para comparar
taxas_infeccao = [0.35, 0.55, 0.75]

figura, eixos = plt.subplots(1, len(taxas_infeccao), figsize=(18,6), sharey=True)

for i, taxa in enumerate(taxas_infeccao):
    historico = executar_simulacao(taxa_infeccao=taxa)

    tempos = [linha["tempo"] for linha in historico]
    desinformado = [linha["desinformado"] for linha in historico]
    ciente = [linha["ciente"] for linha in historico]
    interessado = [linha["interessado"] for linha in historico]
    abandonou = [linha["abandonou"] for linha in historico]

    eixos[i].plot(tempos, desinformado, label="Desinformado",  color="black")
    eixos[i].plot(tempos, ciente, label="Ciente",  color="red")
    eixos[i].plot(tempos, interessado, label="Interessado",  color="green")
    eixos[i].plot(tempos, abandonou, label="Abandonou",  color="blue")

    eixos[i].set_title(f"Taxa de infecção = {taxa}")
    eixos[i].set_xlabel("Tempo")
    eixos[i].grid(True)

eixos[0].set_ylabel("Proporção de indivíduos")
eixos[-1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
plt.suptitle("Comparação da evolução dos estados em diferentes taxas de infecção")
plt.show()
# fim do gráfico 1

# Gráfico 2
def grafico2():
    iniciais = [1, 10, 100]              # número inicial de interessados
    probabilidades = [0, 0.1, 1]         # probabilidade de religação da rede
    passos = 70                          # número de passos da simulação
    cores = ["black", "red", "green"]

    figura, eixos = plt.subplots(1, len(probabilidades), figsize=(18,6), sharey=True)

    for i, p in enumerate(probabilidades):
        for j, n in enumerate(iniciais):
            historico = executar_simulacao_iniciais(
                probabilidade_religacao=p,
                taxa_infeccao=0.35,
                quantidade_passos=passos,
                iniciais_interessados=n
            )

            tempos = [linha["tempo"] for linha in historico]
            abandonou = [linha["abandonou"] for linha in historico]

            eixos[i].plot(tempos, abandonou, label=f"{n} iniciais", color=cores[j])

        eixos[i].set_title(f"Probabilidade de religação = {p}")
        eixos[i].set_xlabel("Tempo")
        eixos[i].grid(True)

    eixos[0].set_ylabel("Número de abandonados")
    eixos[-1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.suptitle("Influência do número inicial de interessados na propagação")
    plt.show()

grafico2()
#fim do gráfico 2

#Grafico 3
def grafico3():
    taxas_infeccao = [0.1, 0.5, 0.7] # diferentes taxas de infeccção
    limites_memoria = [1, 3, 5] #limite de memória
    passos = 70

    # largura das barras
    largura = 0.25
    x = np.arange(len(taxas_infeccao))

    # cores para cada limite
    cores = {1: "red", 3: "green", 5: "blue"}

    figura, eixo = plt.subplots(figsize=(8,6))

    for idx, limite in enumerate(limites_memoria):
        abandonados_finais = []
        for taxa in taxas_infeccao:
            historico = executar_simulacao_iniciais(
                probabilidade_religacao=0.1,
                taxa_infeccao=taxa,
                quantidade_passos=passos,
                limite_memoria=limite,
                limite_atenuacao=0.5,
                iniciais_interessados=1
            )
            abandonados_finais.append(historico[-1]["abandonou"])

        # desloca cada grupo de barras
        eixo.bar(
            x + idx*largura,
            abandonados_finais,
            width=largura,
            color=cores[limite],
            label=f"limite memória = {limite}"
        )

    eixo.set_xticks(x + largura)
    eixo.set_xticklabels([str(t) for t in taxas_infeccao])
    eixo.set_xlabel("Taxa de infecção")
    eixo.set_ylabel("Número de abandonados")
    eixo.set_title("Número de abandonados sob diferentes limites de memória")
    eixo.legend()
    plt.show()

grafico3()
#fim do grafico 3

