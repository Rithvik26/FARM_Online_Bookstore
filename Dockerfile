# Stage 1: Build React.js frontend
FROM node:14 as frontend-build

# Set the working directory
WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY frontend/my-frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY frontend/my-frontend ./

# Print the contents of the current directory
RUN ls -al

# Build the React app
RUN npm run build


# Stage 2: Build FastAPI backend
FROM python:3.9 as backend-build

# Set environment variables for MongoDB
ENV MONGO_HOST=localhost
ENV MONGO_PORT=27017
ENV MONGO_DB=bookdb

# Set the working directory in the container
WORKDIR /app/backend

# Copy the dependencies file to the working directory
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code to the working directory
COPY backend .

# Copy the built frontend files from the frontend-build stage into the backend directory
COPY --from=frontend-build /app/frontend/build /app/backend/static

# Expose the port that the FastAPI application runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
