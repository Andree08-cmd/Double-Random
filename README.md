# 📊 Conjunto de Dados FEN Balanceado para Xadrez Aleatório Duplo (960²)

Este repositório contém um script Python de código aberto e um conjunto de dados verificado de **445 FENs perfeitamente balanceadas** para a variante **Xadrez Aleatório Duplo (960²)**. 

O objetivo central deste projeto é mitigar e eliminar os desequilíbrios severos intrínsecos ao primeiro turno, bem como as assimetrias críticas entre as forças das peças brancas e pretas, utilizando uma abordagem algorítmica rigorosa de **filtragem em três estágios baseada no Stockfish**.

---

## 🛠️ Metodologia de Filtragem (Algoritmo em Funil)

### 🛑 1. Estágio I: Triagem Inicial (Filtro de Erros Estruturais)
* **Configuração da Engine:** `Profundidade = 12` | `MultiPV = 1`
* **Critério Estrito de Corte:** A avaliação matemática deve situar-se estritamente no intervalo entre **−1.0** e **+1.0**.

> **Justificativa Técnica:** Uma profundidade de 12 *plies* (semi-lances) equivale a uma análise preditiva de aproximadamente 6 lances completos à frente para cada lado. Se o Stockfish detectar uma vantagem superior a 1,0 peão de material equivalente em um horizonte tão curto, a posição inicial apresenta um grave e irrecuperável desequilíbrio estrutural. Posições que falham neste estágio são descartadas imediatamente, otimizando o tempo e o custo de processamento computacional.

---

### 🎯 2. Estágio II: Refinamento Dinâmico de Opções (O "Ponto Ideal")
* **Configuração da Engine:** `Profundidade = 23` | `MultiPV = 5`
* **Critérios Estritos de Corte:**
  * As **2 melhores linhas/jogadas candidatas** devem pontuar estritamente entre **−0.23** e **+0.23**.
  * Os **próximos 3 movimentos subsequentes** (*slots* MultiPV 3, 4 e 5) devem orbitar estritamente entre **−0.8** e **+0.8**.

> **Justificativa Técnica:** Para garantir a jogabilidade humana, não basta que uma posição seja estritamente equilibrada em apenas uma única linha perfeita de computador (o que geraria lances únicos e engessados). O uso de `MultiPV = 5` garante que ambos os jogadores disponham de múltiplos caminhos estratégicos viáveis, ricos e saudáveis. Limitar as duas melhores escolhas próximas a **0.0** blinda o equilíbrio matemático puro, enquanto a tolerância de até **±0.8** nas demais linhas assegura dinamismo tático, permitindo escolhas intuitivas sem punir instantaneamente o enxadrista humano por não encontrar a jogada exata da máquina.

---

###  3. Estágio III: Validação Avançada (Selo de Qualidade Final)
* **Configuração da Engine:** `Profundidade = 30` | `MultiPV = 5`
* **Critério Estrito de Corte:** Confirmação e estabilização absoluta de todos os limites estabelecidos no **Estágio II**.

> **Justificativa Técnica:** A profundidade de 30 *plies* atua como uma barreira matemática definitiva contra o célebre **"efeito horizonte"** — fenômeno em que os motores de xadrez alteram drasticamente suas avaliações ao calcular camadas mais profundas. Se a estabilidade, a solidez e o equilíbrio simétrico do FEN resistirem e se mantiverem firmes sob o escrutínio profundo de nível de Super Grande Mestre, a FEN é oficialmente homologada e selada para o ambiente de alta competição.
