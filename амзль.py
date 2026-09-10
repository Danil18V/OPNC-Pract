class Playlist:
    def __init__(self):
        self.songs=[]

    def add_song(self,name,duration):
        self.songs.append({
            "name": name,
            "duration": duration
        })

    def remove_song(self,name):
        for i,song in enumerate(self.songs):
            if song['name'] == name:
                del self.songs[i]
                return

    def total_duration(self):
        return sum(song['duration'] for song in self.songs)

    def __len__(self):
        return len(self.songs)

    def show_songs(self):
        if not self.songs:
            print('Плейлист пуст')
            return
        print('Список песен в плейлисте:')
        for song in self.songs:
            print(f'Песня {song["name"]} длительность {song["duration"]} секунд ')


if __name__ == "__main__":
    playlist = Playlist()

    playlist.add_song("Доедешь пиши", 500)
    playlist.add_song("Отмели", 300)
    playlist.add_song("Была не была", 450)

    print("\nСписок песен после добавления:")
    playlist.show_songs()

    print(f"\nКоличество песен: {len(playlist)}")
    print(f"Общая длительность: {playlist.total_duration()} сек")


    playlist.remove_song("Отмели")
    print("\nПосле удаления Отмели:")
    playlist.show_songs()


    playlist.remove_song(" Зять ")
    print("\nПосле попытки удалить песню Зять:")
    playlist.show_songs()