# # -------- Build Stage --------
# FROM node:20-alpine AS builder

# WORKDIR /app

# # Install dependencies
# COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
# RUN \
#   if [ -f package-lock.json ]; then npm ci; \
#   elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install; \
#   elif [ -f yarn.lock ]; then yarn install; \
#   else npm install; fi

# # Copy source code
# COPY . .

# # Build Next.js app
# RUN npm run build

# # -------- Runtime Stage --------
# FROM node:20-alpine AS runner

# WORKDIR /app

# ENV NODE_ENV=production

# COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
# RUN \
#   if [ -f package-lock.json ]; then npm ci; \
#   elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install; \
#   elif [ -f yarn.lock ]; then yarn install; \
#   else npm install; fi

# COPY --from=builder /app/.next/standalone ./
# COPY --from=builder /app/.next/static ./.next/static
# COPY --from=builder /app/public ./public
# COPY --from=builder /app/package.json ./package.json
# COPY --from=builder /app/next.config.* ./

# EXPOSE 3000

# local
# CMD ["npm", "start"]



# -------- Build Stage --------
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install; \
  elif [ -f yarn.lock ]; then yarn install; \
  else npm install; fi

# Copy source code
COPY . .

# Build Next.js app
RUN npm run build

# -------- Runtime Stage --------
FROM node:20-alpine AS runner

WORKDIR /app

# Cloud Run uses the PORT environment variable (defaulting to 8080)
ENV NODE_ENV=production
ENV PORT=8080
ENV HOSTNAME="0.0.0.0"

# You DO NOT need to run 'npm ci' here.
# The standalone folder already includes necessary node_modules.

# Copy standalone build and static files
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Cloud Run - Start the server from the root directory
# Since we copied standalone contents to './', server.js is in the root.
CMD ["node", "server.js"]
