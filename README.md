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

## Notes:

##### Solved Issues:

- Docker by deafult do not support ipv 6 and works on ipv 4
- Supabase free tier does not support free tier privileges for ipv 4
- To fix this prbalem, we have to change the settings of docker to ipv 6:

Go to Settings -> Docker Engine -> Add the following configuration:

`{
  "experimental": true,
  "ipv6": true,
  "fixed-cidr-v6": "fd00::/80",
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  }
}`

- In docker-compose.yml, add the following configuration:

`networks:
  default:
    external:
      name: smarttutor_ipv6`

## License

MIT
