FROM node:20

# Python
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

COPY package*.json ./
RUN npm install

# Copiar requirements.txt desde la carpeta ai
COPY ai/requirements.txt ./ai/
RUN pip3 install --break-system-packages -r ./ai/requirements.txt

COPY . .

EXPOSE 3000
EXPOSE 8000