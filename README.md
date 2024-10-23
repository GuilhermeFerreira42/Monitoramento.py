# Observador de Pastas em Python

Este projeto é um script em Python que observa uma pasta específica e copia os arquivos para outra pasta configurada. Ele foi projetado para rodar em segundo plano com uma interface gráfica simples.

## Funcionalidades

- Observa uma pasta especificada pelo usuário.
- Copia arquivos automaticamente para uma pasta de destino configurada.
- Possibilidade de copiar a estrutura inteira da pasta ou apenas os arquivos.
- Logs de operações são exibidos na interface e salvos em um arquivo `log.txt`.
- Rodar em segundo plano e minimizar na tray do Windows (a ser implementado).

## Instalação

1. Clone este repositório para o seu ambiente local:
    ```sh
    git clone https://github.com/seu-usuario/observador-de-pastas.git
    cd observador-de-pastas
    ```

2. Instale as dependências necessárias:
    ```sh
    pip install watchdog
    ```

## Uso

1. Execute o script principal:
    ```sh
    python main.py
    ```

2. Na interface gráfica:
    - Selecione a pasta para observar.
    - Selecione a pasta de destino.
    - Escolha se deseja copiar a estrutura inteira da pasta ou apenas os arquivos.
    - Clique em "Iniciar" para começar a monitorar. O botão ficará verde indicando que o monitoramento está ativo.
    - Clique em "Parar" para interromper o monitoramento. O botão voltará à cor original.

## Estrutura do Projeto

```plaintext
observador-de-pastas/
│
├── monitoramento.py  # Script principal com a lógica de observação e cópia
├── log.txt           # Arquivo de log gerado automaticamente durante a execução
└── README.md         # Este arquivo README
