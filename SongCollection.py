class SongCollection:
    def __init__(self):
        self.songs = []

    def add_song(self, element):
        self.songs.append(element)

    def sort_songs(self):  # Sortowanie piosenek ignorując emotikonę 🔥 🎂 🎅  w tytule
        self.songs.sort(
            key=lambda element: element.Title.replace('🔥', '').replace('🎂', '').replace('🎅', '').replace('⭐', "")
        )

    def assign_numbers(self, prefix):
        for index, element in enumerate(self.songs, start=1):
            element.Number = f'{prefix}{index}'

    def get_songs_by_difficulty(self, *levels):
        # Zwraca listę piosenek o określonych poziomach trudności
        return [element for element in self.songs if element.Level in levels]

    def __iter__(self):
        # Zwraca iterator do listy piosenek
        self._index = 0  # Ustawienie początkowego indeksu dla iteracji
        return self

    def __next__(self):
        # Zwraca kolejny element z listy piosenek
        if self._index < len(self.songs):
            result = self.songs[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration

    def get_new_songs(self):
        return [element for element in self.songs if element.new]

    def count_songs(self):
        return len(self.songs)  # Zwraca liczbę piosenek w liście