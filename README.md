# Sistemas de votos em BlockChain

Este projeto implementa um sistema distribuído de votação utilizando tecnologia blockchain, garantindo segurança, transparência e descentralização no processo de registro e validação de votos. A solução inclui uma interface intuitiva para eleitores, sincronização entre nós da rede (peers) e um backend robusto para gerenciar a cadeia de blocos. Ideal para explorar conceitos de blockchain e sua aplicação prática em sistemas distribuídos.

## 🚀 Começando

Essas instruções permitirão que você obtenha uma cópia do projeto em operação na sua máquina local para fins de desenvolvimento e teste.

### 📋 Pré-requisitos

Para conseguir utilizar esse projeto, você precisa possuir o *Docker Desktop* instalado. Para instalá-lo é só seguir a [documentação de instalação do *Docker*](https://docs.docker.com/get-started/get-docker/).

### 🔧 Instalação

Baixe o repositório em sua máquina :)

## ⚙️ Executando os testes

Para conseguir utilizar o sistema de votos, siga o passo a passo:

* Abra o *Docker Desktop* devidamente instalado e faça o login
* Abra a pasta do repositório no terminal da sua máquina
* Digite o seguinte comando: **⁠docker-compose up --build**
* Após isso, abra no navegador a URL: [https:localhost](http://localhost)
* Realize votos como os seguintes votantes nos candidatos abaixo:
  * Votantes: [voter1, voter2, voter3, ..., voter9, voter10]
  * Candidatos: 111, 222, 333
* Teste a validação de votos!

> Caso deseje reiniciar o projeto, ou ocorra algum erro pela já existência dos peers, você pode utilizar o seguinte comando para limpar o *conteiner* do *Docker*: **docker-compose down**, ou limpar manualmente no aplicativo *Docker Desktop*.
