from slowapi import Limiter
from slowapi.util import get_remote_address

# Ini satpam kita. Dia ngenalin user berdasarkan IP Address.
limiter = Limiter(key_func=get_remote_address)