# Gerenciador de Livros

Aplicação desktop para o acervo de uma biblioteca: cadastro de livros, usuários e funcionários, reservas, leitura no local, retirada e devolução.

Atividade de integração com banco de dados da UC05 (Senac). Feita com **Python**, **PySide6** (telas) e **SQLite** (banco de dados).

Este README é um **roteiro**: cada etapa mostra **o que foi feito** e **por quê**, na ordem em que o programa foi construído.

---

## Como rodar

```
cd gerenciador-livros
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

No Linux ou macOS, a ativação é `source .venv/bin/activate`.

**Login de teste:** usuário `admin`, senha `admin`.

O banco `livros.db` é criado sozinho na primeira execução.

---

## Organização dos arquivos

Cada arquivo tem uma única responsabilidade. Assim, uma mudança na tela não quebra o banco, e uma regra nova não exige mexer na tela.

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Liga tudo: tema, login, abertura e janela principal |
| `schema.sql` | Estrutura do banco: tabelas, restrições e a visão de disponibilidade |
| `banco.py` | Todo o SQL do programa. Só ele conversa com o banco |
| `validacao.py` | Regras dos dados digitados (livro, pessoa, CPF, datas) |
| `servicos.py` | Regras de negócio: reserva, uso, devolução, prazos e limites |
| `seguranca.py` | Proteção da senha |
| `login.py` | Tela de login |
| `janela_principal.py` | Janela dos livros (cadastro à esquerda, lista à direita) |
| `pessoas.py` | Tela de usuários e de funcionários |
| `reservas.py` | Tela de reservas |
| `usos.py` | Tela de livros em uso |
| `tema.py` | Temas claro, escuro e biblioteca |
| `livro.py`, `abertura.py`, `virada.py`, `icones.py` | Visual de livro: capa, animações de abrir e de virar a página, ícones |
| `gerar_textura.py` | Ferramenta: gera a textura de papel (`imagens/papel.png`) |
| `importar_json.py` | Ferramenta: importa pessoas de um arquivo JSON para o banco |
| `SEED/` | Dados fictícios de teste (funcionários e usuários) e instruções de importação |

---

# Roteiro de construção

## Parte 1 — Base do programa

### Etapa 1 — Ambiente virtual e `.gitignore`

**O que foi feito:** criado o ambiente virtual (`.venv`), instalado o PySide6, gerado o `requirements.txt` e criado o `.gitignore`.

**Por quê:** o ambiente virtual separa as bibliotecas deste projeto das do computador. O `requirements.txt` permite instalar as mesmas versões em outra máquina. O `.gitignore` deixa fora do Git o que não é código: a `.venv`, os arquivos compilados e o banco `*.db` (cada máquina cria o seu).

### Etapa 2 — Janela principal vazia

**O que foi feito:** `main.py` cria a aplicação e abre uma janela sem conteúdo.

**Por quê:** conferir que o PySide6 funciona antes de construir qualquer coisa em cima.

### Etapa 3 — Formulário e botões

**O que foi feito:** campos Título, Autor, Ano e ISBN, e os botões Cadastrar, Atualizar, Excluir e Limpar.

**Por quê:** montar primeiro a tela e só depois dar função aos botões. Cada problema aparece isolado: primeiro o visual, depois o comportamento.

### Etapa 4 — Pesquisa, tabela e barra de mensagens

**O que foi feito:** campo de pesquisa, tabela de livros e uma barra no rodapé para mensagens.

**Por quê:** a barra de mensagens avisa o resultado de cada ação sem abrir janelas que interrompem o trabalho.

---

## Parte 2 — Integração com o banco de dados

### Etapa 5 — `banco.py` e listagem

**O que foi feito:** criado o `banco.py` com a conexão ao SQLite e a função que lista os livros. A tabela da tela passou a mostrar o que está no banco.

**Por quê:** todo o SQL fica num arquivo só. A tela chama funções como `listar_livros` e não precisa saber SQL.

### Etapa 6 — Cadastro com validação separada

**O que foi feito:** o botão Cadastrar grava o livro. As regras ficam no `validacao.py`: título e autor obrigatórios, ano só com números.

**Por quê:**
- **Validação fora da tela:** as regras são funções simples, fáceis de testar e de reaproveitar.
- **`ErroValidacao(campo, mensagem)`:** o erro diz qual campo está errado, e a tela leva o cursor direto para ele.
- **Parâmetros `?` no SQL:** o valor digitado nunca é colado dentro do comando. Isso evita injeção de SQL.

### Etapa 7 — Pesquisa, mostrar todos e seleção

**O que foi feito:** pesquisa por título ou autor, botão Mostrar todos, e clicar numa linha preenche o formulário.

**Por quê:** selecionar na tabela é o caminho para atualizar e excluir. O ID do livro fica guardado na linha, sem o usuário precisar digitar.

### Etapa 8 — Excluir e atualizar

**O que foi feito:** exclusão e atualização do livro selecionado, com confirmação antes de gravar.

**Por quê:** são ações que não dá para desfazer. A confirmação evita perder dados por um clique errado.

---

## Parte 3 — Visual

### Etapa 9 — Duas colunas e temas

**O que foi feito:** cadastro à esquerda e lista à direita. Três temas: claro, escuro e biblioteca (tons de marrom). O tema escolhido fica salvo.

**Por quê:**
- **Duas colunas:** formulário e resultado ficam visíveis ao mesmo tempo.
- **Um dicionário de cores por tema:** a folha de estilo é uma só, e as cores entram nela como variáveis. Criar um tema novo é só acrescentar um dicionário.
- **`QSettings`:** guarda a escolha entre uma execução e outra.

### Etapa 10 — Janela em formato de livro aberto

**O que foi feito:** a janela perdeu a moldura do sistema e virou um livro aberto: capa, lombada no meio e cada coluna como uma página.

**Por quê:** dar identidade ao programa. Sem a moldura, a barra de título, o minimizar, o fechar e o arrastar da janela foram refeitos dentro do próprio livro.

### Etapa 11 — Animação de abertura e de fechamento

**O que foi feito:** ao iniciar, um livro se abre antes da janela aparecer. Ao sair, ele se fecha.

**Por quê:** a animação é desenhada por código (`QPainter`), sem vídeo nem imagem externa, e usa as cores do tema atual.

### Etapa 12 — Textura, ícones, fita e folhas

**O que foi feito:**
- textura de papel nas páginas do tema biblioteca;
- ícones nos botões;
- fita marcadora saindo da lombada;
- pilha de folhas na borda, dando espessura ao livro.

**Por quê:**
- **Textura gerada por código** (`gerar_textura.py`): não depende de imagem de terceiros.
- **Ícones em SVG pintados com a cor do tema** (`icones.py`): o mesmo desenho serve para os três temas.

### Etapa 13 — Citação de Paulo Freire

**O que foi feito:** citação abaixo do cadastro, no formato acadêmico (autor, ano e página).

> "Se a educação sozinha não transforma a sociedade, sem ela tampouco a sociedade muda." (Freire, 2000, p. 67)

**Por quê:** ligar o programa ao seu propósito, uma biblioteca, respeitando a norma de citação.

---

## Parte 4 — Entidades do acervo

### Etapa 14 — Modelo de dados (`schema.sql`)

**O que foi feito:** criadas as tabelas do acervo.

| Tabela | O que guarda |
|---|---|
| `livro` | Título, autor, ano, ISBN e quantidade de exemplares |
| `usuario` | Quem lê: nome, CPF, e-mail; endereço e nascimento opcionais |
| `funcionario` | Quem atende: todos os campos obrigatórios, mais o código |
| `reserva` | Pedido para guardar livros: usuário, funcionário, prazo e situação |
| `livro_reservado` | Os livros de cada reserva |
| `livro_em_uso` | Livro com o usuário: no local ou retirada, início, prazo e fim |
| `acesso` | Login do sistema |

**Por quê:**
- **`livro_em_uso` separado da reserva:** um livro pode ser usado sem reserva (a pessoa chega e pega). O uso é registrado sempre, com ou sem reserva.
- **Regras dentro do banco** (`CHECK`, `UNIQUE`, chaves estrangeiras): mesmo que o programa erre, o banco recusa dado inválido. Exemplos: CPF com 11 dígitos, retirada sempre com prazo de devolução, o mesmo usuário não fica com o mesmo livro duas vezes.
- **Visão `disponibilidade`:** disponíveis = exemplares − em uso − em reservas ativas. O número é sempre calculado, nunca guardado, então não fica desatualizado.
- **Migração:** quem já tinha livros cadastrados não perde nada; a coluna de quantidade é acrescentada ao abrir.

### Etapa 15 — Login com senha protegida

**O que foi feito:** tela de login ao abrir o programa. Para testes, `admin` / `admin`. Depois de 5 tentativas erradas, o programa fecha.

**Por quê:**
- **A senha não é guardada.** O banco guarda só o resumo (hash PBKDF2) com sal. Quem abrir o arquivo do banco não descobre a senha.
- **Mensagem única** ("Usuário ou senha incorretos"): não revela qual dos dois está errado.

### Etapa 16 — Usuários e funcionários

**O que foi feito:** uma tela para cada, com cadastro, busca, atualização e desativação. O funcionário recebe um código automático: iniciais de cada nome + 2 últimos dígitos do CPF.

Exemplo: Claudio de Araujo Pereira Rodrigues, CPF terminado em 30 → **CAPR30**.

**Por quê:**
- **Uma tela para os dois tipos:** os campos são os mesmos; muda só o que é obrigatório. Evita código repetido.
- **Poucos campos obrigatórios para o usuário:** cadastro rápido no balcão.
- **Desativar em vez de excluir:** a pessoa pode ter histórico de reservas e usos, que não pode sumir.
- **Código curto:** fácil de lembrar e rápido de digitar a cada operação.

### Etapa 17 — Código do funcionário nas operações de livro

**O que foi feito:** cadastrar, alterar e excluir livro pedem o código de um funcionário ativo.

**Por quê:** só funcionários mexem no acervo, e cada alteração tem um responsável.

### Etapa 18 — Exemplares e disponíveis

**O que foi feito:** o livro ganhou o campo quantidade. A tabela mostra Exemplares e Disponíveis. A quantidade não pode ficar menor que os exemplares que estão fora.

**Por quê:** evitar reservar ou entregar um livro que não está na estante.

---

## Parte 5 — Movimentação do acervo

### Etapa 19 — Reservas

**O que foi feito:** tela de reservas. O funcionário digita o seu código, acha o usuário pelo nome ou CPF e marca os livros. Dá para cancelar uma reserva ativa.

Regras:
- a reserva vale **2 dias**; depois disso expira sozinha e libera os exemplares;
- cada usuário pode ter até **3 livros** ao mesmo tempo (em uso + reservados);
- só aparecem livros com exemplar disponível.

**Por quê:**
- **`servicos.py`:** as regras de negócio ficam fora da tela. A tela só pede os dados e mostra o resultado.
- **Transação:** a reserva e os seus livros são gravados juntos. Se um livro falhar, nada é gravado.
- **Busca por parte do nome ou do CPF:** menos digitação no atendimento.

### Etapa 20 — Livros em uso e devolução

**O que foi feito:** tela Em uso. O funcionário entrega o livro para **ler no local** ou para **retirar** (14 dias para devolver) e registra a devolução. Na tela de reservas, o botão Retirar transforma a reserva em retirada.

**Por quê:**
- **Devolver é preencher a data de fim.** O registro continua no banco como histórico, e o exemplar volta a ficar disponível.
- **Reserva → retirada numa transação só:** o livro nunca é contado duas vezes (reservado e em uso) nem some da contagem.
- **Mesmas regras da reserva:** código do funcionário, limite de 3 livros e exemplar disponível.

### Etapa 21 — Destaque para atrasados

**O que foi feito:** na tela Em uso, o livro com prazo vencido aparece como "atrasado", em negrito e em cor de alerta.

**Por quê:** o funcionário enxerga os atrasos sem ler linha por linha. Cada tema tem a sua cor de alerta, com contraste conferido. A palavra "atrasado" continua escrita, então a informação não depende só da cor.

---

## Parte 6 — Evolução

### Etapa 22 — Telas dentro do livro, com virada de página

**O que foi feito:** as telas de Usuários, Funcionários, Reservas e Em uso deixaram de abrir em janelas por cima. Cada uma ocupa as duas páginas do livro, e trocar de aba vira a página até ela. A folha que vira é curva, com frente, verso e sombra.

**Por quê:**
- **Tudo dentro do livro:** o programa mantém a mesma identidade em todas as telas, sem janelas soltas.
- **Pilha de conteúdos por página** (`QStackedWidget`): cada página guarda um conteúdo por tela e mostra um de cada vez. A lombada e a fita ficam sempre no mesmo lugar.
- **Animação com duas "fotos"** (`virada.py`): o programa fotografa as páginas antes e depois da troca e desenha a folha por cima. Assim a animação não depende do conteúdo de cada tela.
- **Folha em tiras:** a folha é desenhada em 60 tiras verticais, cada uma com a sua inclinação. Perto da lombada ela vem atrasada e a ponta vai na frente; é isso que cria a curva.
- **Direção:** aba à direita vira para a frente, aba à esquerda vira para trás, como ao folhear.

### Etapa 23 — Dados de teste (SEED)

**O que foi feito:** criada a ferramenta `importar_json.py`, que lê um arquivo JSON de pessoas e grava no banco como usuários ou funcionários. A pasta `SEED/` guarda 5 funcionários e 30 usuários fictícios, com as instruções de uso.

**Por quê:**
- **Testar com volume:** pesquisa, reservas e limites só são bem testados com várias pessoas cadastradas.
- **Mesma validação da tela:** o importador usa `validar_pessoa`, então nenhum dado entra no banco fora das regras.
- **CPF repetido é pulado:** rodar duas vezes não duplica ninguém.
- **Só os campos do sistema:** do arquivo entram nome, CPF, e-mail, nascimento e endereço; o resto é ignorado.

### Etapa 24 — Máscara do CPF

**O que foi feito:** nas telas, o CPF aparece só com o final visível: `***.***.247-25`.

**Por quê:** o código do funcionário já mostra os 2 últimos dígitos do CPF. A máscara mostra o mesmo trecho final, então o código e a máscara juntos não revelam mais do que cada um sozinho, e 6 dígitos ficam sempre escondidos de quem olha a tela.

---

## Regras do sistema (resumo)

| Regra | Valor |
|---|---|
| Prazo para retirar uma reserva | 2 dias |
| Prazo para devolver uma retirada | 14 dias |
| Livros por usuário ao mesmo tempo | 3 (em uso + reservados) |
| Quem altera o acervo | Funcionário ativo, pelo código |
| Pessoas e livros com histórico | São desativados ou preservados, não excluídos |
| CPF na tela | Só o final visível: `***.***.247-25` |

Os prazos e o limite são constantes no topo do `servicos.py`.

---

## Avaliação da estrutura do projeto

Análise da organização atual: o que está certo e o que pode melhorar.

### O que está certo

A separação por responsabilidade (camadas) é respeitada nos imports:

- `banco.py` só fala SQL e não importa nada de tela;
- `validacao.py` não depende de banco nem de tela;
- `servicos.py` usa o banco e a validação, mas não a tela;
- as telas chamam os serviços e o banco, nunca o contrário.

**Por que importa:** uma mudança na tela não quebra o banco, e uma regra nova não exige mexer na tela.

### O que pode melhorar

**1. Todos os arquivos estão numa pasta só.** Telas, regras, banco, visual e ferramentas ficam misturados. A organização existe no código, mas não aparece nas pastas. Uma divisão possível:

```
gerenciador-livros/
├── main.py
├── requirements.txt
├── dados/        banco.py, schema.sql, seguranca.py
├── regras/       validacao.py, servicos.py
├── telas/        janela_principal.py, login.py, pessoas.py, reservas.py, usos.py
├── visual/       tema.py, livro.py, abertura.py, virada.py, icones.py, imagens/
└── ferramentas/  importar_json.py, gerar_textura.py, SEED/
```

**2. `janela_principal.py` faz coisas demais.** É o maior arquivo do projeto, com mais que o dobro das linhas de qualquer outra tela. Ele monta a moldura do livro (abas, tema, virada de página) e também é a tela de livros (formulário, tabela, cadastrar, excluir). A tela de livros poderia ter o seu próprio arquivo, como já acontece com `pessoas.py` e `reservas.py`.

**3. Código repetido entre `reservas.py` e `usos.py`.** A busca de usuário, a lista de livros com filtro e o aviso de erro são quase iguais nos dois. Se uma regra mudar, é preciso lembrar de mudar nos dois lugares.

**4. Detalhes menores.**
- A pasta `SEED` está em maiúsculas; o resto do projeto usa minúsculas.
- As ferramentas de uso único (`importar_json.py`, `gerar_textura.py`) estão junto com o programa.
- O nome da classe `Janela_Livros` mistura dois estilos; o padrão do Python é `JanelaLivros`.

### Vale a pena mudar?

| Mudança | Ganho | Risco |
|---|---|---|
| Detalhes menores (4) | Pequeno, mas visível | Quase nenhum |
| Separar a tela de livros (2) | Arquivo principal mais simples | Médio |
| Unificar o código repetido (3) | Manutenção mais fácil | Médio |
| Criar pastas (1) | Organização visível | Médio a alto: muda todos os imports e os caminhos de `schema.sql`, `livros.db` e `imagens/` |

**Conclusão:** as camadas estão corretas, que é o mais importante numa integração com banco de dados. As melhorias são de organização, não de funcionamento. A ordem mais segura é: detalhes menores, depois separar a tela de livros, e por último as pastas, sempre testando tudo antes de cada commit.

---

## Referência

FREIRE, Paulo. **Pedagogia da indignação**: cartas pedagógicas e outros escritos. São Paulo: Editora UNESP, 2000.
