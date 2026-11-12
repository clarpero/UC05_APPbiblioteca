SEED - dados de teste

Esta pasta guarda dados fictícios para preencher o banco e testar o programa
sem cadastrar pessoa por pessoa.

  FUNCIONARIOS.json   5 funcionários
  USUARIOS.json       30 usuários

Os dados foram gerados no gerador de pessoas do 4devs (4devs.com.br).
São fictícios: não pertencem a pessoas reais.


COMO IMPORTAR

Na pasta gerenciador-livros, com o programa fechado e a .venv ativada:

  python importar_json.py SEED/FUNCIONARIOS.json funcionario
  python importar_json.py SEED/USUARIOS.json

A saída mostra uma linha por pessoa:

  OK      a pessoa foi gravada (para funcionário, mostra o código gerado)
  PULADO  a pessoa não foi gravada, com o motivo

No fim aparece o total, por exemplo: "30 de 30 pessoa(s) importada(s) como usuario."


O QUE O IMPORTADOR FAZ, E POR QUÊ

1. Usa a mesma validação da tela de cadastro (validar_pessoa).
   Por quê: nenhum dado entra no banco fora das regras. O CPF é conferido,
   o e-mail é validado e a data passa de dd/mm/aaaa para o formato do banco.

2. Pula CPF que já está cadastrado.
   Por quê: rodar o comando duas vezes não duplica ninguém.

3. Gera o código do funcionário (iniciais + 2 últimos dígitos do CPF).
   Por quê: é a mesma regra do cadastro pela tela.

4. Aproveita só os campos que o sistema tem.
   Do JSON entram: nome, cpf, email, data_nasc e o endereço, montado com
   endereco, numero, bairro, cidade e estado.
   Os outros campos do arquivo (rg, senha, mae, pai, telefone etc.) são
   ignorados e não vão para o banco.


USAR OUTRO ARQUIVO

Qualquer JSON no mesmo formato do 4devs funciona:

  python importar_json.py caminho/do/arquivo.json               (usuários)
  python importar_json.py caminho/do/arquivo.json funcionario   (funcionários)

Se todas as pessoas saírem como PULADO, os nomes dos campos do arquivo são
diferentes dos esperados (nome, cpf, email, data_nasc, endereco, numero,
bairro, cidade, estado).
