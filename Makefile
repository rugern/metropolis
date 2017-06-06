install:
	pip3 install -r requirements.txt

save:
	pip3 freeze > requirements.txt

test:
	python3 ./tests/orderbook.test.py
	python3 ./tests/bank.test.py

benchmark:
	# Add @profile to functions you want to test
	# Note: Modify to take command as argument
	kernprof -l -v sample/main.py
