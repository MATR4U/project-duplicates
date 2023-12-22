FROM node:alpine
WORKDIR /app
EXPOSE 3000
COPY package.json ./
COPY package-lock.json ./
COPY ./ ./
RUN npm i
CMD ["npm", "run", "start"]