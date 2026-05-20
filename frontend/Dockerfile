FROM node:20-alpine

RUN apk add --no-cache libc6-compat

WORKDIR /app

# Install deps layer (cache-friendly)
COPY package.json package-lock.json* ./
RUN npm ci 2>/dev/null || npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
