emojis = """🐵 Monkey
🦍 Gorilla
🦧 Orangutan
🐶 Dog
🐺 Wolf
🦊 Fox
🐱 Cat
🦁 Lion
🐯 Tiger
🐴 Horse
🦄 Unicorn
🐮 Cow
🐷 Pig
🐐 Goat
🐫 Camel
🦙 Llama
🦒 Giraffe
🐘 Elephant
🦏 Rhinoceros
🦛 Hippopotamus
🐭 Mouse
🐹 Hamster
🐰 Rabbit
🦇 Bat
🐻 Bear
🐨 Koala
🐼 Panda
🦦 Otter
🦃 Turkey
🐔 Chicken
🐦 Bird
🐧 Penguin
🦉 Owl
🦜 Parrot
🐸 Frog
🐲 Dragon
🦖 T-Rex
🐳 Whale
🐬 Dolphin
🐟 Fish
🐙 Octopus
🦋 Butterfly
🐛 Bug
🐜 Ant
🐝 Honeybee
🦀 Crab"""

animal = emojis.split('\n')
split_up = [e.split(' ') for e in animal]
emojis = [e[0] for e in split_up] 
emoji_names = [e[1] for e in split_up]

print(emojis)
print(emoji_names)