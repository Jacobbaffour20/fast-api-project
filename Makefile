.PHONY: run

run:
	@uvicorn main:app --host 0.0.0.0 --port 8000 --reload
run-server:
	@uvicorn main:app --host 0.0.0.0 --port 8000
