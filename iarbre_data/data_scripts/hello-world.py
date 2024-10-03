# docker run -it --rm --name my-running-script -v /c/Users/ICG4702/Documents/developpements/arb/tests:/usr/src/myapp -w /usr/src/myapp python:3 python hello-world.py

import time

print('Hello, World from Docker on OpenShift !')
time.sleep(5)