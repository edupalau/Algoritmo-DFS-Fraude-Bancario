"""Shared configuration values for the fraud analysis project."""

COL_SENDER = "Sender Account ID"
COL_RECEIVER = "Receiver Account ID"
COL_AMOUNT = "Transaction Amount"

DEFAULT_MIN_AMOUNT = 10_000
DEFAULT_MIN_TRANSACTIONS = 3
DEFAULT_MAX_TRANSACTIONS = 10

SMURFING_THRESHOLD = 0.80
