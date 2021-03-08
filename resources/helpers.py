import math

from resources.data_objects import suffixes


def human_format(num, precision=2):  # Convert 1023 to something like 1.02K
    m = int(math.log10(num) // 3) if num != 0 else 0  # avoid domain error by handling zeros
    return f'{num / 1000.0 ** m:.{precision}f}{suffixes[m]}'.strip('.00')


def get_offset(string: str, start_index: int) -> int:
    return len(string.encode('utf-16-le')) // 2 - len(string) + start_index
