# hi-world


## Scope
To implement a circuit breaker that trips the circuit when the drop rate in a service is higher than a defined parameter. Also implements the immediate restore logic when recovering from a tripped state.


##Setup
```pip install -r /path/to/requirements.txt```


## Usage

1. Download the cb module
2. Run a redis server instance `redis-server`
2. Import the circuitBreaker module into your code
```
from cb.circuitbreaker import circuitBreaker
```
3. Create a circuitBreaker object
```
cb = circuitBreaker()
```
4. Instead of standard `http requests`, use `cb.getReq` or `cb.postReq`
5. Takes care drops and runs restore when needed. Change configs in cb/config.py to customize


## Technologies Used
* Python
* Flask
* SQLAlchemy
* redis
* <s> boto SQS </s>
* <s> Celery </s>
