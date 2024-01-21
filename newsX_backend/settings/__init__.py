import os


if os.environ.get("ENV_NAME") == 'PROD':
    from .production import *
elif os.environ.get("ENV_NAME") == 'DEV':
    from .staging import *
else:
    from .local import *

