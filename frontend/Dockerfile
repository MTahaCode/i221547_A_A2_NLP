# Development Dockerfile for React
FROM node:20-alpine

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the React dev server port
EXPOSE 3000

# Start the React development server
CMD ["npm", "run", "dev"]
