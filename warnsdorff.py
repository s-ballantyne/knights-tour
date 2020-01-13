import sys
import typing
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
parser.add_argument("-n", "--files", type=int, default=5, help="optional: number of ranks")
parser.add_argument("-m", "--ranks", type=int, default=0, help="optional: number of files, defaults to number of ranks (-n)")
parser.add_argument("-s", "--start", type=str, default="a1", help="optional: starting square")

args = parser.parse_args()

logging.basicConfig(
	level=logging.DEBUG if args.verbose else logging.INFO,
	format= '[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s' if args.verbose else "%(message)s",
	datefmt='%H:%M:%S'
)

files = args.files
ranks = args.ranks or files
sq_count = files * ranks
sq_max = sq_count - 1
sq_start = (ord(args.start[0]) - ord('a')) + 8 * (int(args.start[1]) - 1)

if files <= 0:
	logging.fatal(f"expected parameter 'files' to be a positive integer, got '{files}' instead")
	parser.print_help(sys.stderr)
	quit()

if ranks <= 0:
	logging.fatal(f"expected parameter 'ranks' to be a positive integer, got '{ranks}' instead")
	parser.print_help(sys.stderr)
	quit()

if not (0 <= sq_start <= sq_max):
	logging.fatal(f"starting square '{args.start}' ({sq_start}) is not valid")
	parser.print_help(sys.stderr)
	quit()

logging.info(f"using {files}x{ranks} board size")
logging.info(f"starting square is '{args.start}' ({sq_start})")

def rank_of(sq: int) -> int:
	return sq // ranks

def file_of(sq: int) -> int:
	return sq % files

def format_square(sq: int) -> str:
	return f"{chr(file_of(sq) + ord('a'))}{rank_of(sq) + 1}"

def distance(sq1: int, sq2: int) -> int:
	return max(abs(file_of(sq1) - file_of(sq2)), abs(rank_of(sq1) - rank_of(sq2)))

def step_attacks(sq: int, dirs: typing.Iterable[int]):
	for d in dirs:
		s = sq + d
		if 0 <= s <= sq_max and distance(sq, s) <= 2:
			yield s


logging.debug("generating attack table")
knight_directions = [2 * files + 1, 2 * files - 1, 2 + files, -2 + files, -2 * files + 1, -2 * files - 1, 2 - files, -2 - files]
knight_attacks = [list(step_attacks(sq, knight_directions)) for sq in range(sq_count)]

logging.debug("generating board")
board = [False] * sq_count		

def filtered_attacks(sq: int):
	return filter(lambda s: not board[s], knight_attacks[sq])

def open_tour(sq: int, res=[]):
	board[sq] = True
	res.append(format_square(sq))

	attacks = list(filtered_attacks(sq))
	degrees = [len(list(filtered_attacks(s))) for s in attacks]
	if len(degrees) > 0:
		min_degree = min(degrees)
		next_sq = attacks[degrees.index(min_degree)]
		open_tour(next_sq)
	else:
		logging.info("-".join(res))

open_tour(sq_start)
