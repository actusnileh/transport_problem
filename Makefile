DC = docker compose
BACKEND_FILE = docker_compose/backend.yaml
FRONTEND_FILE = docker_compose/frontend.yaml

.PHONY: all
all:
	${DC} -f ${FRONTEND_FILE} up --build -d
	${DC} -f ${BACKEND_FILE} up --build -d

.PHONY: drop-all
drop-all:
	${DC} -f ${BACKEND_FILE} -f ${FRONTEND_FILE}  down

.PHONY: logs
logs:
	${DC} -f ${BACKEND_FILE} -f ${FRONTEND_FILE} logs -f