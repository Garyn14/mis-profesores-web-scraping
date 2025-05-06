"""Progress display utilities"""
import sys


def print_progress(current: int, total: int, message: str = ""):
    """Display progress bar with a message"""
    bar_length = 50
    progress = float(current) / total
    block = int(round(bar_length * progress))

    text = (f"\rProgress: [{'=' * block}{' ' * (bar_length - block)}] "
            f"{current}/{total} - {message}")
    sys.stdout.write(text)
    sys.stdout.flush()

    if current == total:
        print()