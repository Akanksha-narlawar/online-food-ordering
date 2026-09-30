# Online Food Ordering Platform

A Docker Compose based food ordering application with:

- Nginx reverse proxy
- Flask Order API
- PostgreSQL database

## Architecture

Customer → Nginx → Order API → PostgreSQL

## Services

### Nginx
Receives customer requests and forwards them to the Order API.

### Order API
Provides APIs to create and retrieve food orders.

### PostgreSQL
Stores order data using a persistent Docker volume.

## API Endpoints

### Health Check

```text
GET /health