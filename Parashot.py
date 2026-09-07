from Text import NarrationText, Word
import pandas as pd
from pathlib import Path
import colorsys
import HebrewNumbers
#from PDF import ParashahBookletPDF
#from Overlay import EpisodeOverlay
#from Audio import ParashahAudio

ROOT = Path(__file__).parent

PARASHOT_CSV = ROOT / "parashot.csv"
EPISODES_CSV = ROOT / "episodes.csv"
MD_PATH = ROOT / "parashot.md"

class Paragraph:
	def __init__(self, episode, number):
		self.episode = episode
		self.number = number
		self.verses = []

	@property
	def layout(self):
		return self.episode.layout[self.number - 1]


#	def __getitem__(self, index):
#		return self.verses[index]

#	def __len__(self):
#		return len(self.verses)

	def slides(self):
		slides = []
		current = []
		for verse in self.verses:
			# If the verse text starts with '$', close current slide and start new
			if verse.text.startswith('$'):
				if current:
					slides.append(current)
				current = []
				# Remove the '$' from the verse's text for the slide
				verse.text = verse.text[1:]  # strip the leading marker
			current.append(verse)
		if current:
			slides.append(current)
		return slides

	def __repr__(self):
		return f"Paragraph({self.episode.parashah.number}.{self.episode.number}.{self.number}, {len(self.verses)} verses)"

class ParashahEpisode():
	def __init__(self, parashah, number, start_verse, end_verse, metadata=None):
		self.parashah = parashah
		self.number = number
		self.start_verse = start_verse
		self.end_verse = end_verse
		self.english_title = metadata.get('english_title', '') if metadata else ''
		self.hebrew_title = metadata.get('hebrew_title', '') if metadata else ''
		self.paragraphs = []
		#self.overlay = EpisodeOverlay(self)
		self.load()

	def load(self):
		start_chapter, start_verse = map(int, self.start_verse.split('.'))
		end_chapter, end_verse = map(int, self.end_verse.split('.'))
		self.verses = self.parashah.parashot.bible.verses(
			self.parashah.book,#.number,
			start_chapter, start_verse,
			end_chapter, end_verse
		)
		#print(self.paragraphs)
		self.paragraphs = []


	@property
	def color(self):
		parashah_color = self.parashah.color
		total_episodes = len(self.parashah.episodes)
		episode_index = self.parashah.episodes.index(self)
		r, g, b = parashah_color
		hue_shift = (episode_index / total_episodes) * 30 - 15
		h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
		h = (h + hue_shift/360) % 1.0
		r, g, b = colorsys.hls_to_rgb(h, l, s)
		return (int(r*255), int(g*255), int(b*255))

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)


	@property
	def layout(self):
		original = []
		for paragraph in self.paragraphs:
			lines = []
			for verse in paragraph.verses:
				for line_words in verse.words:
					line = [Word(word, verse) for word in line_words]
					lines.append(line)
			original.append(lines)
		layout = []
		for paragraph in original:
			new_paragraph = []
			if not paragraph:
				continue
			current_merged_line = paragraph[0]
			for i in range(1, len(paragraph)):
				line = paragraph[i]
				prev_line_words = paragraph[i-1]
				if line[0].verse.number == prev_line_words[0].verse.number:
					new_paragraph.append(current_merged_line)
					current_merged_line = line
				else:
					current_merged_line.extend(line)
			if current_merged_line:
				new_paragraph.append(current_merged_line)
			layout.append(new_paragraph)
		return layout


	@property
	def vlayout(self):
		"""Vertical layout: split paragraphs at verses starting with '$' and build lines."""
		layout = []
		for paragraph in self.paragraphs:
			# Split paragraph.verses into groups where a verse starts with '$'
			groups = []
			current = []
			for verse in paragraph.verses:
				if verse.text.startswith('$'):
					if current:
						groups.append(current)
					current = []
				current.append(verse)
			if current:
				groups.append(current)
	
			# For each group, build lines and merge lines from the same verse
			for verses in groups:
				lines = []
				for verse in verses:
					for line_words in verse.words:
						line = [Word(word, verse) for word in line_words]
						lines.append(line)
				# Merge consecutive lines that belong to the same verse
				merged = []
				if not lines:
					continue
				current_line = lines[0]
				for i in range(1, len(lines)):
					next_line = lines[i]
					if next_line[0].verse.number == current_line[0].verse.number:
						merged.append(current_line)
						current_line = next_line
					else:
						current_line.extend(next_line)
				merged.append(current_line)
				layout.append(merged)
		return layout




#	def __getitem__(self, index):
#		return self.paragraphs[index]

#	def __len__(self):
#		return len(self.paragraphs)

	def __repr__(self):
		return f"ParashahEpisode({self.parashah.number}.{self.number}, {self.start_verse}-{self.end_verse})"

























class Parashah(NarrationText):
	def __init__(self, parashot, metadata):
		self.parashot = parashot
		self.metadata = metadata
		self.number = int(metadata['number'])
		self.english_name = metadata['english_name']
		self.hebrew_name = metadata['hebrew_name']
		self.book = parashot.bible.books[int(metadata['book']) - 1]
		NarrationText.__init__(self, f"parashot/{self.number:02d}.md")
		self.english_title = ""
		self.english_description = ""
		self.hebrew_title = ""
		self.hebrew_description = ""
		self.episodes = []
		self.load()


	@property
	def color(self):
		book_color = self.book.color
		parashot_in_book = [p for p in self.parashot._items if p.book.number == self.book.number]
		total_parashot_in_book = len(parashot_in_book)
		parashah_index = [p.number for p in parashot_in_book].index(self.number)
		progress = parashah_index / (total_parashot_in_book - 1) if total_parashot_in_book > 1 else 0.5
		r, g, b = book_color
		lightness = 0.4 + (0.4 * progress)
		h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
		l = max(0, min(1, l * lightness))
		r, g, b = colorsys.hls_to_rgb(h, l, s)
		return (int(r*255), int(g*255), int(b*255))

	def pdf(self):
		ParashahBookletPDF(self).generate()

	def load(self):
		#EPISODES_CSV = "db/episodes.csv"
#		csv_path = Path()
#		if csv_path.exists():
#		try:
		episodes_df = pd.read_csv(EPISODES_CSV, dtype={
			'start_chapter': int, 'start_verse': int,
			'end_chapter': int, 'end_verse': int
		})
		parashah_episodes = episodes_df[episodes_df['parashah'] == self.number]
		if len(parashah_episodes) > 0:
			self.episodes = []
			for _, row in parashah_episodes.iterrows():
				start_verse = f"{row['start_chapter']}.{row['start_verse']}"
				end_verse = f"{row['end_chapter']}.{row['end_verse']}"
				episode = ParashahEpisode(self, row['number'], start_verse, end_verse, row.to_dict())
				self.episodes.append(episode)
		else:
			default_metadata = {'english_title': self.english_name, 'hebrew_title': self.hebrew_name}
			self.episodes = [ParashahEpisode(self, 1, self.metadata['start_verse'], self.metadata['end_verse'], default_metadata)]
	#except Exception as e:
	#	print(f"❌ Error loading parashah {self.number}: {e}")
	#	default_metadata = {'english_title': self.english_name, 'hebrew_title': self.hebrew_name}
#		self.episodes = [ParashahEpisode(self, 1, self.metadata['start_verse'], self.metadata['end_verse'], default_metadata)]
	#else:
	#print(f"❌ Episodes CSV not found: {csv_path}")

#			default_metadata = {'english_title': self.english_name, 'hebrew_title': self.hebrew_name}
#			self.episodes = [ParashahEpisode(self, 1, self.metadata['start_verse'], self.metadata['end_verse'], default_metadata)]

		content = self.read()
		if content:
			verse_index = 0
			episode_index = 0
			for paragraph_data in content:
				while (episode_index < len(self.episodes) and
						verse_index < len(self.episodes[episode_index].verses)):
					episode_index += 1
					verse_index = 0
				if episode_index >= len(self.episodes):
					break
				episode = self.episodes[episode_index]
				paragraph = Paragraph(episode, len(episode.paragraphs) + 1)

				for verse_lines in paragraph_data[episode_index]:
					print (f"verse index {verse_index}")
					if verse_index < len(episode.verses):
						lines = verse_lines#[1]
						paragraph.verses[verse_index].text = '\n'.join(lines)
						#verse = episode.verses[verse_index]
						#self.parashot.bible.books[verse.chapter.book.number - 1].chapters[verse.chapter.number - 1].verses[verse.number - 1] = '\n'.join(lines)
					
					paragraph.verses.append(episode.verses[verse_index])
					verse_index += 1
				if paragraph.verses:
					episode.paragraphs.append(paragraph)
		else:
			#print ("NO")
			#print (content)
			#exit()
			for episode in self.episodes:
				paragraph = Paragraph(episode, 1)
				paragraph.verses = episode.verses
				episode.paragraphs = [paragraph]

	@property
	def markdown(self):
		return super().markdown

	@markdown.setter
	def markdown(self, content):
		super(Parashah, self.__class__).markdown.fset(self, content)

	@markdown.deleter
	def markdown(self):
		super(Parashah, self.__class__).markdown.fdel(self)

	@property
	def verses(self):
		verses = []
		for episode in self.episodes:
			for paragraph in episode.paragraphs:
				verses.extend(paragraph.verses)
		return verses

	def __getitem__(self, index):
		return self.episodes[index]

	def __len__(self):
		return len(self.episodes)

	def __repr__(self):
		return f"Parashah({self.number}: {self.english_name})"


#	@property
#	def layout(self):
#		#return [line for episode in self.episodes for line in episode.layout]
#		return [layout for episode in self.episodes for layout in episode.layout]

	@property
	def paragraphs(self):
		return [paragraph for episode in self.episodes for paragraph in episode.paragraphs]

#	@property
#	def slug(self):
#		return self.english_name.lower()



class Parashot:
	def __init__(self, bible):
		self.bible = bible
		self._items = []
		self.load()

	def load(self):
		print ("HERE")
		print (PARASHOT_CSV)
		#PARASHOT_CSV = "db/parashot.csv"
		parashot_df = pd.read_csv(PARASHOT_CSV, dtype={
			'start_chapter': int, 'start_verse': int,
			'end_chapter': int, 'end_verse': int
		})
		self._items = []
		for _, row in parashot_df.iterrows():
			start_verse = f"{row['start_chapter']}.{row['start_verse']}"
			end_verse = f"{row['end_chapter']}.{row['end_verse']}"
			metadata = {
				'number': row['number'],
				'english_name': row['english_name'],
				'hebrew_name': row['hebrew_name'],
				'book': row['book'],
				'start_verse': start_verse,
				'end_verse': end_verse
			}
			parashah = Parashah(self, metadata)
			self._items.append(parashah)

		print ("HERE2")
		md_path = MD_PATH
		content = md_path.read_text(encoding='utf-8')
		paragraphs = content.strip().split('\n\n')
		i = 0
		while i < len(paragraphs):
			english = paragraphs[i]
			hebrew = paragraphs[i + 1]
			en_title, en_desc = english.split('•', 1)
			he_title, he_desc = hebrew.split('•', 1)
			parashah_index = i // 2
			self._items[parashah_index].english_title = en_title.strip()
			self._items[parashah_index].english_description = en_desc.strip()
			self._items[parashah_index].hebrew_title = he_title.strip()
			self._items[parashah_index].hebrew_description = he_desc.strip()
			i += 2

	def __getitem__(self, key):
		if isinstance(key, str):
			return next(p for p in self._items if p.english_name.lower() == key.lower())
		return self._items[key]


if __name__ == "__main__":
	from Bible import Bible
	bible = Bible()
	parashot = Parashot(bible)
	parashah = parashot._items[0]
	print(f"Parashah: {parashah.hebrew_name} ({parashah.english_name})")
	if parashah.episodes:
		episode = parashah.episodes[0]
		print(f"Episode: {episode.hebrew_title} ({episode.english_title})")
		if episode.paragraphs:
			paragraph = episode.paragraphs[0]
			print(f"Paragraph: {paragraph.number}")
			if paragraph.verses:
				verse = paragraph.verses[0]
				print("Verse text (custom):")
				print(verse.text)
				print("Verse orig_text (raw):")
				print(verse.orig_text)
				print("Verse bare_text (cleaned):")
				print(verse.bare_text)
