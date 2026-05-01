FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* ./

RUN npm ci || yarn install || npm install

COPY . .

RUN npm run build

FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/package.json /app/package-lock.json* /app/yarn.lock* ./

RUN npm ci --only=production || yarn install --production || npm install --only=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
