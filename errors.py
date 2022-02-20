class InvalidCommandUsage(Exception):
    """Generic exception for improper command usage.\n
    Used to indicate a need for printing help on a command/subcommand tree."""
    def __init__(self, command, subcommand=None):
        self.command = command
        self.subcommand = subcommand
