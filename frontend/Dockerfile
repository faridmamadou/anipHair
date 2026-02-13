FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Command to run the application in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
