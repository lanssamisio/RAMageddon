# PyZelda

Jogo 2D inspirado em Zelda desenvolvido em Python com Pygame. [......]

Projeto desenvolvido para a disciplina **Introdução à Programação** do Centro de Informática (CIn), Universidade Federal de Pernambuco (UFPE).

## Sobre o jogo

- Tela fixa de **800 x 600 pixels** a **60 FPS**.
- Movimento em quatro direções com animação baseada em tempo.
- Colisões por uma grade de tiles de 25 x 25 pixels.
- Espada colecionável que libera um portal animado.
- Navegação entre seis salas por bordas abertas e pelo portal.
- Transições suaves com efeito de pixelização.
- Sistema de depuração integrado ao jogo.

## Ideação e objetivo do projeto



- **Ideia e inspiração:**  
- **Objetivo principal:**  
- **Regras e progressão:**  
- **Fluxo pretendido:**  
- **Personagem e elementos:**  

## Controles

| Ação | Teclas |
| :--- | :--- |
| Mover para cima | `W` ou `↑` |
| Mover para baixo | `S` ou `↓` |
| Mover para esquerda | `A` ou `←` |
| Mover para direita | `D` ou `→` |
| Atacar | `Espaço` ou `J` |

### Depuração

| Tecla | Função |
| :---: | :--- |
| `F1` | Liga ou desliga o modo de depuração |
| `F2` | Mostra colisões e aberturas |
| `F3` | Mostra a grade de tiles |
| `F4` | Mostra hitboxes e entidades |
| `F5` | Mostra FPS, posição e estado atual |

## Como executar

### Pré-requisitos

- Python 3
- `pip`

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Linux e macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Estrutura do projeto

```text
PyZelda/
├── assets/
│   └── images/
│       ├── andar_baixo.png
│       ├── andar_baixo.txt
│       ├── andar_cima.png
│       ├── andar_cima.txt
│       ├── mapa inicial.png
│       └── portal.png
├── src/
│   ├── carregador.py
│   ├── config.py
│   ├── debug.py
│   ├── jogador.py
│   ├── salas.py
│   ├── sprites.py
│   └── transicao.py
├── main.py
├── requirements.txt
└── README.md
```

### Principais módulos

- **`main.py`**: inicializa o Pygame, executa o loop principal e integra movimento, itens, salas e interface.
- **`src/config.py`**: reúne resolução, FPS, tamanho dos tiles, portas, cores e configurações da transição.
- **`src/jogador.py`**: implementa movimento, colisões, animações e ataque.
- **`src/salas.py`**: define o mapa das seis salas, paredes, itens e portal.
- **`src/transicao.py`**: aplica o efeito de pixelização durante a troca de salas.
- **`src/debug.py`**: fornece visualizações do estado interno e das colisões.
- **`src/carregador.py`**: carrega e recorta os frames dos sprites a partir dos arquivos `.png` e `.txt`.
- **`src/sprites.py`**: divide a spritesheet do portal em quadros individuais.

## Arquitetura do projeto

O código inteiro foi dividido nas seguintes partes com o intuito de deixá-lo mais organizado, intuitivo e inteligível:

- **Assets**: Pasta em que se encontram todas as imagens utilizadas pelo jogo. Em `assets/images` estão os sprites do personagem, o fundo da primeira sala e a spritesheet animada do portal. Os arquivos `.txt` associados aos personagens armazenam as coordenadas dos quadros de cada animação.
- **Classes**: Pasta em que estão localizadas as principais entidades e comportamentos do jogo. Os arquivos da pasta `src` são organizados em módulos orientados a objetos e definem o jogador, as salas, os itens, o portal e a transição entre áreas. É nessa divisão que ficam a movimentação do personagem, a animação, as colisões e a criação dos elementos visuais.
- **Functions**: Funções auxiliares distribuídas pelos módulos de `src`. Em `src/carregador.py`, por exemplo, estão as funções responsáveis por ler coordenadas e carregar os quadros das animações; em `src/salas.py`, por verificar saídas e criar as salas; e em `src/sprites.py`, por separar uma spritesheet em quadros individuais.
- **Config**: Arquivo em que as constantes gerais são definidas. `src/config.py` concentra o tamanho da tela, os FPS, o tamanho dos tiles, as posições das portas, as cores, os blocos da transição e a duração dos efeitos.
- **Engine**: Arquivo principal que faz o jogo entrar em funcionamento contínuo. O `main.py` cria o Pygame, inicializa a tela, produz as salas e executa o loop responsável por ler eventos, atualizar o jogador e os estados da partida e renderizar o cenário a cada frame.
- **Main**: Arquivo que contém a função `main()` e o bloco `if __name__ == "__main__":`. Esse trecho garante que o jogo seja iniciado apenas quando `main.py` for executado diretamente como programa principal.

## Organização das salas

```text
[6] ← [5] ← [4]
             ↑
[1] → [2] → [3]
```

A **Sala 1** apresenta o mapa inicial, a espada e o portal. Após coletar a espada, o portal é ativado e permite entrar na **Sala 2**. As salas restantes são conectadas pelas bordas abertas do mapa.

## Tecnologias utilizadas

- **Python**: linguagem principal.
- **Pygame Community Edition (`pygame-ce`)**: janela, eventos, desenho, animação e controle de FPS.
- **Módulos padrão de Python**: `math` e `pathlib`.

## Conceitos de Introdução à Programação

O projeto aplica diversos conceitos vistos ao longo da disciplina:

- **Condicionais**: verificam teclas pressionadas, colisões, coleta de itens e estados da transição.
- **Laços**: atualizam o jogo, percorrem mapas e processam os frames das animações.
- **Listas e tuplas**: armazenam configurações, coordenadas, quadros e dados das salas.
- **Dicionários**: associam direções às animações e identificadores às configurações das salas.
- **Funções e modularização**: separaram responsabilidades em módulos reutilizáveis.
- **Classes e objetos**: modelam o jogador, itens, portais, salas e transições.
- **Colisões**: usam `pygame.Rect` e tiles sólidas próximas ao personagem.
- **Vetores**: representam posição e direção por meio de `pygame.Vector2`.
- **Tempo independente de FPS**: usa `dt` para movimento e animações consistentes.

### Exemplos no código

```python
# src/jogador.py: direção selecionada pela pilha das teclas pressionadas
if self.pilha_teclas:
    direcao = pygame.Vector2(TECLAS_DIRECAO[self.pilha_teclas[-1]])
```

```python
# src/salas.py: geração do mapa por linha e coluna
linha_mapa += "#" if eh_borda and not eh_abertura else "."
```

```python
# src/jogador.py: movimento com tempo independente da quantidade de frames
self.posicao.x += direcao.x * self.VELOCIDADE * dt
```

```python
# src/transicao.py: troca da sala no pico do efeito pixelado
if self.estado == "saindo":
    self.estado = "entrando"
    return True
```

## Desafios, erros e aprendizados

>**Dificuldades com o GitHub:** A colaboração eficaz no GitHub é crucial para o desenvolvimento de software em equipe. No entanto, membros da equipe não estavam familiarizados com essa plataforma e tiveram dificuldade para utilizá-la adequadamente. Isso levou a dificuldades na coordenação do trabalho.

### Desafios técnicos

- **Colisões por eixo:** impedir que o personagem atravesse paredes exigiu separar o movimento horizontal do vertical e corrigir o `Rect` após cada contato.
- **Movimento consistente:** substituir incrementos fixos por movimento multiplicado por `dt` evitou que a velocidade mudasse em máquinas com FPS diferente.
- **Direções sem sprites laterais:** como os arquivos disponíveis são voltados para cima e baixo, as animações laterais reutilizam o sprite inferior com espelhamento horizontal.
- **Arquivos de animação:** coordenadas diferentes podem produzir folhas incompletas ou índices inválidos; o carregador verifica a existência dos arquivos e usa um desenho provisório quando necessário.
- **Transição entre salas:** a troca precisa ocorrer no pico da pixelização para que o jogador não enxergue a alteração diretamente.
- **Consistência do posicionamento:** cada entrada de sala precisava posicionar o personagem corretamente dentro da tela, em vez de mantê-lo fora da borda.
- **Desempenho:** procurar todas as tiles do mapa a cada movimento seria desnecessário, então `tiles_solidos_perto()` limita a busca aos retângulos próximos.

### Erros encontrados e soluções

- **Sprite não aparecia:** o caminho dos arquivos era validado e os arquivos necessários foram organizados em `assets/images/`, com o nome sem extensão usado pelo carregador.
- **Jogador atravessava cantos das paredes:** as colisões foram resolvidas separadamente nos eixos X e Y.
- **Animação acelerava ou desacelerava:** o tempo dos quadros passou a ser controlado por `dt` e não pela quantidade de iterações do loop.
- **Teclas de movimento conflitavam:** foi criada uma pilha para priorizar a última direção acionada.
- **Sala não trocava no momento correto:** a transição recebeu estados explícitos de saída e entrada.
- **Depuração alterava a lógica do jogo:** as representações visuais foram separadas da física e agrupadas em `src/debug.py`.

### Aprendizados

- Organização em módulos facilita manutenção e trabalho em equipe.
- Constantes centralizadas reduzem números mágicos espalhados pelo código.
- Testar colisões, movimentação e estados separadamente torna os erros mais fáceis de localizar.
- Assets externos devem ser tratados como recursos que podem faltar ou estar incompletos.
- Ferramentas de depuração ajudam a verificar estados que não ficam visíveis na tela comum.
- Git e GitHub auxiliam a controlar alterações e integrar partes desenvolvidas por integrantes diferentes.

## Divisão de tarefas

> Preencha esta tabela com os nomes e responsabilidades efetivas de cada integrante.

| Integrante | Responsabilidades |
| :--- | :--- |
| **[@lanssamisio](https://github.com/lanssamisio)** | Estrutura geral do projeto e integração das partes; responsável por detalhar ao final as funcionalidades implementadas. |
| **[@Maplely](https://github.com/Maplely)** | Desenvolvimento e apoio às funcionalidades do jogo; responsável por detalhar ao final os módulos implementados. Code Reviwer |
| **[@hrrymnz](https://github.com/hrrymnz)** | Desenvolvimento e apoio às funcionalidades do jogo; responsável pelo relatório. Code Reviwer|

Pode-se organizar a divisão por módulos, por exemplo:

| Área | Possível responsável | Principais entregas |
| :--- | :--- | :--- |
| Arquitetura e loop principal | [Nome do integrante] | Inicialização, integração dos módulos e gerenciamento de estados. |
| Jogador e controles | [Nome do integrante] | Movimento, animações, colisões e ataque. |
| Salas e mapa | [Nome do integrante] | Configuração das salas, paredes, portas e itens. |
| Interface e assets | [Nome do integrante] | Sprites, fundo, portal e apresentação visual. |
| Transições e depuração | [Nome do integrante] | Pixelização, troca de salas e ferramentas de F1 a F5. |
| Documentação e testes | [Nome do integrante] | README, revisão do código e testes de execução. |

## Equipe

| GitHub |
| :--- |
| [@lanssamisio](https://github.com/lanssamisio) |
| [@Maplely](https://github.com/Maplely) |
| [@hrrymnz](https://github.com/hrrymnz) |

---

Projeto acadêmico desenvolvido no CIn–UFPE.
```