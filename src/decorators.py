import time
from sodapy import Socrata
from functools import wraps
from utils import setup_logger

MAX_TIMEOUT = 60

def setup(times=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.log:
                self.log = setup_logger(self.domain)

            self.log.info(f"Task Started for {self.domain}: {func.__name__}")

            for i in range(times):
                try:
                    if not self.client:
                        print(f"Initializing client for {self.domain}...")
                        self.client = Socrata(self.domain, self.token, timeout=self.timeout)
                    elif self.timeout > self.client.timeout:
                        self.client.timeout = self.timeout
                    self.timeout = min(self.timeout*2, MAX_TIMEOUT)

                    result = func(self, *args, **kwargs)
                    
                    self.log.info(f"Task Successful for {self.domain}: {func.__name__}")
                    return result
                except ConnectionError as e:
                    self.log.error(f"{self.domain} failed to connect. Is the domain correct?")
                    break
                except Exception as e:
                    if i == times - 1:
                        self.log.error(f"Final failure in for {self.domain}'s {func.__name__}: {str(e)}")
                        raise e
                    self.log.warning(f"Attempt {i+1}/{times} failed for {self.domain}'s {func.__name__}: {str(e)}")
                    time.sleep(delay)
        return wrapper
    return decorator