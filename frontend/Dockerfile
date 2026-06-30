# Dev-oriented image for docker-compose. Dependencies (incl. native binaries)
# are installed inside the container; an anonymous volume keeps node_modules
# from being shadowed by the host mount.
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
