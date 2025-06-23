# Constants for RI-Experiment-LLM backend

NUM_ROUNDS = 30
QUALITY_STATES = [40, 55, 70, 85]
PRODUCT_PRICES = [26, 30, 34, 42]

# Quality offsets when the dominated decoy is shown
QUALITY_OFFSETS_WITH_DECOY = [0, 5, -5, -10]
# Quality offsets when no decoy is shown
QUALITY_OFFSETS_NO_DECOY = [0, 5, -5]

# Cost arms
FREE = "FREE"
PRICE = "PRICE"
DELAY = "DELAY"
COST_ARMS = [FREE, PRICE, DELAY]

# Pricing for GPT replies under the PRICE arm
TOKEN_LIMIT = 75
QUERY_COST_PRICE = 0.05  # dollars per reply <= TOKEN_LIMIT tokens

# Delay requirement in milliseconds for the DELAY arm
DELAY_MS = 3000

# Payoff calculation helpers
PAYOFF_QUALITY_SCALE = 100

# Keys used for logging prompt/reply interactions
LOG_FIELDS = [
    "session",
    "round",
    "arm",
    "tokens",
    "cost",
]

