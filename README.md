# async_test_project [![Build Status](https://travis-ci.org/heckad/async_test_project.svg?branch=master)](https://travis-ci.com/heckad/async_test_project)

## Installing
  * Install mongodb
  * Create virtual env 
  * Install dependencies using `pip install -r requirements.txt` (for testing use `requirements_test.txt`)

## Running
  * Add `MONGO_HOST` and `MONGO_PORT`(if not set will be using default port) to env variables
  * Run by `python main.py`
  
## Testing 
  * Install mongodb with admin user
  * Add `MONGO_HOST`, `MONGO_PORT`(not necessary), `MONGO_USERNAME` equal admin login and `MONGO_PASSWORD` equal admin password
  * Run by `python -m pytest`

## Check code code coverage
  * Make all in testing section except the last action
  * Run by `python -m coverage run -m pytest`
