FROM node:20-alpine
WORKDIR /app

COPY Business-Layer/Express-Server/package*.json ./
WORKDIR /app/Business-Layer/Express-Server
RUN npm install

WORKDIR /app
COPY Business-Layer/Express-Server ./Business-Layer/Express-Server
COPY Presentation-Layer/public ./Presentation-Layer/public

EXPOSE 80

WORKDIR /app/Business-Layer/Express-Server
CMD ["npm", "run", "start", "--", "--host", "0.0.0.0"]
