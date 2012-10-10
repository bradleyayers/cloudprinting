__version__ = "0.3.2"

from .auth import OAuth2
try:
    from .auth import ClientLoginAuth
except ImportError:
    pass
from .client import delete_job, get_job, list_jobs, list_printers, submit_job
