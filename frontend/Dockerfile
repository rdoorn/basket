FROM node:22-slim
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile
COPY . .
EXPOSE 8173
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "8173"]
