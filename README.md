

# Neuron Daily

Fundado em 2024 por ex-diretor de Projetos da Neuron DS&AI, o Neuron Daily oferece boletim diário sobre setores do mercado financeiro e atualidades. O projeto conta com processos automatizados, desde webscraping até o envio de informações para assinantes, utilizando aprendizado de máquina em Python, HTML e CSS. Atualmente, o Neuron Daily conta com mais de 250 leitores.

> Projeto para automação de tarefas com Python: extração, scraping, envio de emails, sumarização e escrita de textos.

## Sumário
- [Visão Geral](#visão-geral)
- [Scripts do Projeto](#scripts-do-projeto)
- [Fluxo de Trabalho com Arquivos XLSX](#fluxo-de-trabalho-com-arquivos-xlsx)
- [Como Executar](#como-executar)
- [Organização e Boas Práticas](#organização-e-boas-práticas)
- [Autor](#autor)

---

## Visão Geral
Este repositório reúne scripts Python para automatizar processos de dados, marketing e geração de conteúdo. Cada script tem uma função específica e pode ser executado individualmente.


## Scripts do Projeto

- **extrair.py**: Extrai e-mails de um arquivo Excel (`inscritos.xlsx`) na aba `Sheet1`, remove duplicados e salva os resultados em dois arquivos: `emails_parte1.xlsx` e `emails.xlsx`. 
  
	**Como usar:**
	1. Certifique-se de que o arquivo `inscritos.xlsx` está na mesma pasta do script.
	2. Execute o script. Os e-mails serão extraídos da coluna "Email" e divididos em dois arquivos para facilitar o envio.
	3. Os arquivos gerados (`emails_parte1.xlsx` e `emails_parte2.xlsx`) serão usados no envio dos boletins.

- **sender.py**: Envia o boletim diário para os e-mails listados em `emails.xlsx`.
  
	**Como usar:**
	1. Certifique-se de que o arquivo `emails.xlsx` está presente na pasta.
	2. Gere o arquivo HTML da newsletter (deve começar com `noticias_` e terminar com `.html`).
	3. Execute o script. Ele irá:
		 - Ler os e-mails do arquivo.
		 - Encontrar o arquivo HTML mais recente.
		 - Enviar o boletim para todos os e-mails usando a conta de marketing configurada no script.
	4. O script mostra no terminal o status do envio e o tempo total gasto.

- **scraping.py**: Realiza scraping de páginas web, automatizando a coleta de dados públicos online.
- **script.py**: Script utilitário ou principal, podendo centralizar funções comuns ou testes.
- **summarizer.py**: Sumariza textos extensos, gerando versões mais curtas e objetivas.
- **writer.py**: Gera ou escreve textos automaticamente, útil para criação de conteúdo.

## Fluxo de Trabalho com Arquivos XLSX

1. Crie um arquivo `.xlsx` com o nome esperado pelo script (verifique nos códigos qual nome é utilizado).
2. Coloque o arquivo `.xlsx` na mesma pasta dos scripts.
3. Execute o script correspondente. Ele irá processar o arquivo conforme a lógica implementada.

## Organização e Boas Práticas

- Mantenha os scripts organizados e documentados.
- Adicione comentários explicativos nos códigos.
- Teste cada script individualmente antes de integrar ao fluxo principal.
- Atualize este README conforme o projeto evoluir.


## Próximos Passos

- Automatizar completamente o processo de envio dos boletins para os assinantes.
- Criar sistema de envio de e-mails por categorias pré-selecionadas pelos usuários, permitindo personalização dos conteúdos recebidos.
- Atingir um número ainda maior de inscritos na newsletter, expandindo o alcance do Neuron Daily.

## Autores

- João Gabriel Gomes Silveira - Criador (2024).
- Rafael Ribeiro dos Santos - Melhorias e Testes (Jan/25 a Abril/25).
- Luiz Henrique Braga Scorzafave - Melhorias e Testes (Abril/25 a Atual).
- Enzo Guilherme Elias da Rocha - Gerencimento e Versionamento (Set/25 a Atual).
- Maria Eduarda Faria - Coordenadora do projeto (Ago/25 a Atual)

---

Sinta-se livre para adaptar este README conforme novas funcionalidades forem adicionadas.
