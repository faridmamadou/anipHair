FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port (if needed, e.g., for health checks or local dashboard)
# EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
