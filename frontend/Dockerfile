FROM node:alpine as builder
# Create a user and group with a specific ID. Avoid using root (user ID 0)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# Switch to this new user
USER appuser
# Set the working directory to /app inside the container
WORKDIR /app
# Copy app files
COPY . .
# Install dependencies (npm ci makes sure the exact versions in the lockfile gets installed)
RUN npm ci 
# Build the app
RUN npm run build

# Bundle static assets with nginx
FROM nginx:alpine as production
# Create a user and group with a specific ID. Avoid using root (user ID 0)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# Switch to this new user
USER appuser
ENV NODE_ENV production
# Copy built assets from `builder` image
COPY --from=builder /app/build /usr/share/nginx/html
# Add your nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port
EXPOSE 80
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]