## Prerequisites

- Python 3.13
-

## Setup

- Clone the repository
- Install dependencies
- Run the application

## Usage

### Terminal commands

- `uvicorn backend.services.ingestion_service.app:app --reload --port 8003`
- `uvicorn backend.services.retrieval_service.app:app --reload --port 8001`
- `uvicorn backend.services.qa_service.app:app --reload --port 8002`
- `uvicorn backend.services.web_search_service.app:app --reload --port 8004`
- `uvicorn backend.services.orchestrator_service.app:app --reload --port 8006`

- The application will return a response

## License

MIT
