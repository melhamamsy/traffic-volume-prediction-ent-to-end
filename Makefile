quality_checks:
	isort .
	black .
	pylint --recursive=y .

unit_test:
	pytest unit_tests/

integration_test: 
	./integration_tests/test_monitoring/run.sh