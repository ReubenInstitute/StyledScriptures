import glob
import os
import unicodedata

FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "text", "psalms")


def list_characters():
	chars = set()
	for path in sorted(glob.glob(os.path.join(FOLDER, "*.md"))):
		with open(path, encoding="utf-8") as f:
			chars.update(f.read())
	for ch in sorted(chars):
		try:
			name = unicodedata.name(ch)
			print(f"U+{ord(ch):04X} {name}")
		except ValueError:
			print(f"U+{ord(ch):04X}")


def check(path):
	problems = []
	with open(path, encoding="utf-8") as f:
		lines = f.read().split("\n")
	while lines and lines[-1] == "":
		lines.pop()
	blank_run = 0
	block = []
	for number, line in enumerate(lines, 1):
		if line == "":
			blank_run += 1
			if blank_run > 1:
				problems.append(f"{path}:{number}: more than one consecutive blank line")
			if block:
				last_number, last_line = block[-1]
				if last_line.endswith("  "):
					problems.append(f"{path}:{last_number}: last line of a block has trailing spaces")
				block = []
			continue
		blank_run = 0
		block.append((number, line))
		text = line
		if line.endswith("  "):
			if line.endswith("   "):
				problems.append(f"{path}:{number}: more than two trailing spaces")
			text = line[:-2]
		else:
			is_last_of_file = number == len(lines)
			next_is_blank = number < len(lines) and lines[number] == ""
			if not (is_last_of_file or next_is_blank):
				problems.append(f"{path}:{number}: text line does not end with two spaces")
		if "  " in text:
			problems.append(f"{path}:{number}: multiple consecutive spaces in text")
		if text.endswith(" "):
			problems.append(f"{path}:{number}: stray trailing space in text")
		if line.endswith("  "):
			continue
	if block:
		last_number, last_line = block[-1]
		if last_line.endswith("  "):
			problems.append(f"{path}:{last_number}: last line of a block has trailing spaces")
	return problems


if __name__ == "__main__":
	total = 0
	for path in sorted(glob.glob(os.path.join(FOLDER, "*.md"))):
		problems = check(path)
		total += len(problems)
		for problem in problems:
			print(problem)
	print(f"{total} problems")
	print()
	list_characters()
