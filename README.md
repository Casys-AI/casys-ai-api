# CASys.AI - Complex Adaptive System of Artificial Intelligence

CASys.AI is an innovative open-source platform designed for modeling, analyzing, and optimizing complex systems. It
integrates advanced artificial intelligence techniques, graph analysis, and non-linear dynamic systems theory to provide
a comprehensive solution for multi-scale challenges across various domains.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)

## Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/casys-ai/casys-ai-api.git
    cd casys-ai-api
    ```

2. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
    ```
    OPENAI_API_KEY=your_openai_api_key
    NEO4J_URI=bolt://neo4j:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_password
    ```

3. Start the application using Docker Compose:
    ```bash
    docker-compose up -d
    ```

This will start all necessary services including the API, Neo4j database, and Redis for task queuing.

## Usage

Once the Docker containers are up and running, the API will be accessible at `http://localhost:8000/docs`.

You can simple interact with it as it's fastAPI

Congigure first the config.yaml where you have to enter the informations of the files that you want to process
Set up the files path

Create the folder
add a new doc or PDF

adjust the prompts for
req.txt = requirements
bdd.txt = Structure
ux.txt = use cases (behavior)

try to extract the entities with project name
if you want to can use the example projects (cdc_1 & crushing_mill), it's better when you have multiple systems
POST http://127.0.0.1:8000/process/{{project_name}}
POST http://127.0.0.1:8000/neo4j-process-project/{{project_name}}

Monitor the task execution with flower
http://localhost:5555/

You can try to render the project that you want :
Acess the BDD
http://localhost:7474/browser/

# sort le graph complet d'un projet

MATCH (p:Project {name: 'your_project'})-[:HAS_DIAGRAM]->(d:Diagram)-[:CONTAINS_ENTITY]->(e:Entity)
RETURN p,d,e

## Features

- Advanced modeling of complex systems _WIP_
- Knowledge graph analysis _WIP_
- AI integration for optimization _WIP_
- Real-time collaboration _TODO_
- Multi-scale knowledge representation _WIP_
- Adaptive artificial intelligence layer _TODO_
- Topological and spectral graph analysis _WIP_
- Non-linear simulation and optimization _TODO_

## Architecture

The project follows a hexagonal (ports and adapters) architecture:

- `src/domain`: Contains business logic and models
- `src/application`: Application services
- `src/adapters`: Adapters for external interfaces (web, persistence)
- `src/infrastructure`: System configuration and initialization

The project uses FastAPI for the REST API, Celery for asynchronous tasks, and Neo4j as the graph database.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes (`git commit -am 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Authors

- **superworldsavior** - *Main developer* - [GitHub Profile](https://github.com/superworldsavior)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.