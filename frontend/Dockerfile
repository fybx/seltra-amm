FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy code
COPY . .

# Run
EXPOSE 3000
CMD ["npm", "start"]
