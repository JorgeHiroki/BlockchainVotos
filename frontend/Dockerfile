# Usar uma imagem base do Nginx
FROM nginx:alpine

# Copiar os arquivos do frontend para o diretório do Nginx
COPY . /usr/share/nginx/html

# Expor a porta 80
EXPOSE 80

# O Nginx já inicia automaticamente, então não precisamos de um CMD explícito