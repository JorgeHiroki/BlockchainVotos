FROM python:3.9-slim

WORKDIR /app

# Copia o arquivo de requirements e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código para o container
COPY . .

# Use o shell para interpretar as variáveis de ambiente e executar o script correto
CMD sh -c "python ${MODE:-central.py}"
