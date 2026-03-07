# Sobre

Esse documento aborda qual o custo estimado da execução da API nos seguintes cenários:

- Migrar para uma API externa comercial (Gemini por exemplo).
- Tunneling do Ollama (Túnel Reverso)
- Servidor VPS Dedicado com GPU (A opção "Correta", porém mais cara)

#### Opção A: Migrar para uma API externa comercial

Em vez de usar o Ollama e rodar o modelo na nuvem (que requer máquinas caras com GPU), utilizar a API do Google (Gemini) por exemplo.

Prós:

- Não precisarei de uma infra cara apenas para a LLM, dessa forma ficaria gratuito hospedar a API.
- Permite a utilização de qualquer modelo da minha escolha.

Contras:

- Gastos com requisições para a API (tokens). Isso pode ser barato caso somente eu faça as otimizações das consultas, porém pode encarecer caso eu exponha o projeto e tenhamos muitos usuários utilizam.

#### Opção B: Tunneling do Ollama (Túnel Reverso)

Hospedar apenas a API (FastAPI) na nuvem num servidor comum, mas apontar as requisições LLM do backend de volta para o seu computador pessoal (onde o Gemma 3 já está instalado).

Prós:

- Zero custos com a execução da LLM.

Contras:

- Necessidade de expor o computador pessoal para a internet.
- Necessita do computador ligado e conectado a internet sempre para que a consulta a LLM funcione.
  se o seu PC pessoal estiver ligado e conectado na internet.

#### Opção C: Servidor VPS Dedicado com GPU

Alugar uma máquina virtual com infraestrutura suficiente para a execução do modelo.

Prós:

- Possível reprodução exata do computador pessoal.
- Permite a instalação do Ollama para execução da LLM.

Contras:

- Teria custos com infra que teria pouca utilização, apenas para a execução do modelo, e com poucos usos.

Observação:
Caso a aplicação receba muitos acessos, pode ser uma opção utilizar essa abordagem.
