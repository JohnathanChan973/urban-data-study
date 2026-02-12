import time
from sodapy import Socrata
from requests.exceptions import ReadTimeout, SSLError
from functools import wraps
from utils import setup_logger

def setup(times=3, delay=2, max_timeout = 60):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.log:
                self.log = setup_logger(self.domain)

            self.log.info(f"Task Started for {self.domain}: {func.__name__}")

            for i in range(times):
                try:
                    if not self.client:
                        self.log.info(f"Initializing client for {self.domain}...")
                        self.client = Socrata(self.domain, self.token, timeout=self.timeout)
                    result = func(self, *args, **kwargs)
                    
                    self.log.info(f"Task Successful for {self.domain}: {func.__name__}")
                    return result
                except ReadTimeout as e:
                    if self.timeout == max_timeout:
                        self.log.error(f"Exceeded max timeout of {max_timeout} for {self.domain}'s {func.__name__}: {str(e)}")
                        raise e
                    self.log.warning(f"Attempt {i+1}/{times} timed out for {self.domain}'s {func.__name__}: {str(e)}")
                    self.timeout = min(self.timeout*2, max_timeout)
                    self.client.timeout = self.timeout
                except ConnectionError or SSLError as e:
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