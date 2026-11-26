.PHONY: all pipeline analysis dashboard test clean

all: pipeline analysis dashboard

pipeline:   ## CSVs brutos -> SQLite (raw, staging, marts)
	python src/pipeline.py

analysis:   ## consultas de negócio -> CSVs, KPIs e gráficos
	python src/analysis.py

dashboard:  ## gera docs/index.html (GitHub Pages)
	python src/build_dashboard.py

test:       ## testes de qualidade de dados
	pytest -q

clean:
	rm -f data/olist.db
