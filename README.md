# Document Intelligence System

## Environment Setup

### Backend Setup
1. Navigate to the `backend` directory
2. Copy the environment example file:
   ```bash
   cp env.example .env
   ```
3. Update the `.env` file with your actual values:
   - `SECRET_KEY`: A secure secret key for your application
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `PINECONE_ENVIRONMENT`: Your Pinecone environment
   - `PINECONE_INDEX_NAME`: Name of your Pinecone index
   - `GOOGLE_API_KEY`: Your Google AI API key
   - `UPSTASH_REDIS_URL`: Redis URL for caching
   - `UPSTASH_REDIS_TOKEN`: Redis authentication token

### Frontend Setup
1. Navigate to the `frontend` directory
2. Copy the environment example file:
   ```bash
   cp env.example .env.local
   ```
3. Update the `.env.local` file:
   - `NEXT_PUBLIC_API_URL`: URL where your backend is running (default: http://localhost:8000)

## Running with Docker
Once you've set up your environment files, you can run both services using:
```bash
docker-compose up --build
```

This will:
- Start the backend on http://localhost:8000
- Start the frontend on http://localhost:3000
- Set up networking between services
- Enable hot-reloading for development

## Development Notes
- The frontend uses Next.js environment variables prefixed with `NEXT_PUBLIC_`
- Environment files (`.env`, `.env.local`) are git-ignored for security
- Example files are provided as templates
- Docker Compose handles environment variable injection for both services
