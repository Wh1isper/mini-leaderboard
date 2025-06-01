from .form import router as form
from .leaderboard import router as leaderboard
from .messgaeboard import router as messageboard
from .vote import router as vote

routers = [leaderboard, messageboard, form, vote]
