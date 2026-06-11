# AC

# Simulação da Propagação de Informação em Redes Sociais Utilizando Autômatos Celulares

## Descrição

Este projeto implementa o artigo *"The Spreading of Information in Online Social Networks through Cellular Automata"* utilizando Python.

O objetivo é simular como informações se propagam em redes sociais online através de um modelo baseado em autômatos celulares e teoria de redes complexas.

O modelo utilizado é o **OSIS (Online Social Networks Information Spreading)**, uma adaptação do modelo epidemiológico SEIR para o contexto de disseminação de informações.

## Estados dos Indivíduos

Cada indivíduo da rede pode assumir um dos seguintes estados:

- **DESINFORMADO**: ainda não teve contato com a informação.
- **CIENTE**: conhece a informação, mas ainda não a compartilha.
- **INTERESSADO**: acredita ou se interessa pela informação e passa a propagá-la.
- **ABANDONOU**: perdeu o interesse e não compartilha mais a informação.

## Estrutura da Rede

A rede social é modelada utilizando o modelo **Small-World de Watts-Strogatz**, que reproduz características observadas em redes sociais reais:

- Alto agrupamento entre indivíduos.
- Pequena distância média entre quaisquer duas pessoas.
- Existência de atalhos que aceleram a propagação da informação.

## Conceitos Implementados

O modelo considera três fatores principais descritos no artigo:

### Efeito Manada

A probabilidade de um indivíduo propagar uma informação aumenta conforme mais vizinhos estejam interessados nela.

### Memória Acumulada

Exposições repetidas à mesma informação aumentam a chance de um indivíduo passar do estado CIENTE para INTERESSADO.

### Atenuação da Informação

Com o passar do tempo o interesse pela informação diminui, levando indivíduos a abandonarem sua propagação.

## Funcionamento da Simulação

A simulação ocorre em passos discretos de tempo.

Em cada passo:

1. Os indivíduos observam o estado de seus vizinhos.
2. As regras de transição do modelo OSIS são aplicadas.
3. Os estados são atualizados simultaneamente.
4. As estatísticas da população são registradas.

## Parâmetros Principais

| Parâmetro | Descrição |
|------------|------------|
| quantidade_individuos | Número total de indivíduos da rede |
| grau_medio | Quantidade média de conexões por indivíduo |
| probabilidade_religacao | Probabilidade de criação de atalhos na rede Small-World |
| quantidade_passos | Número de ciclos simulados |
| taxa_infeccao | Probabilidade base de propagação da informação |
| limite_memoria | Quantidade mínima de exposições necessárias para gerar interesse |
| limite_atenuacao | Valor mínimo de interesse antes do abandono |
| semente | Valor utilizado para reproduzir os mesmos experimentos |

## Objetivo Acadêmico

Este projeto foi desenvolvido como implementação prática do artigo estudado na disciplina de Introdução aos Autômatos Celulares, buscando reproduzir os experimentos, compreender a dinâmica de propagação de informações em redes sociais e analisar os efeitos da estrutura da rede e do comportamento dos indivíduos sobre a disseminação de conteúdo.