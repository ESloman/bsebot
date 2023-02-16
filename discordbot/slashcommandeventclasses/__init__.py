
"""
slashcommandeventclasses/ contains all of the classes for different slach commands
Each file contains a different class for handling a command that isn't dissimilar
to the name of the file
"""

from .bseddies import BSEddies

from .active import BSEddiesActive
from .admin_give import BSEddiesAdminGive
from .autogenerate import BSEddiesAutoGenerate
from .bless import BSEddiesBless
from .close import BSEddiesCloseBet
from .create import BSEddiesCreateBet
from .gift import BSEddiesGift
from .help import BSEddiesHelp
from .highscore import BSEddiesHighScore
from .king import BSEddiesKing
from .king_rename import BSEddiesKingRename
from .leaderboard import BSEddiesLeaderboard
from .pending import BSEddiesPending
from .place import BSEddiesPlaceBet
from .pledge import BSEddiesPledge
from .predict import BSEddiesPredict
from .refresh import BSEddiesRefreshBet
from .stats import BSEddiesStats
from .taxrate import BSEddiesTaxRate
from .transactions import BSEddiesTransactionHistory
from .view import BSEddiesView
