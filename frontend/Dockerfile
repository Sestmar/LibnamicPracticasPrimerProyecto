# Usamos Node.js para el desarrollo
FROM node:20-slim

WORKDIR /app

# Copiamos los archivos de configuración de npm
COPY package*.json ./

# Instalamos las dependencias
RUN npm install

# Copiamos el resto del código
COPY . .

# Exponemos el puerto que usa Vite por defecto
EXPOSE 5173

# Arrancamos en modo desarrollo con acceso externo
CMD ["npm", "run", "dev", "--", "--host"]