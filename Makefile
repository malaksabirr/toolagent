.PHONY: install dev test build sample
install:
	python3 -m venv backend/.venv && . backend/.venv/bin/activate && pip install -r backend/requirements.txt
	cd frontend && npm install
dev:
	./run.sh
test:
	. backend/.venv/bin/activate && cd backend && pytest -q
build:
	cd frontend && npm run build   # le backend sert ensuite l'app sur http://localhost:8000
sample:
	python3 scripts/make_sample_data.py
