import re
from PIL import Image
from wordcloud import WordCloud
from collections import namedtuple
from dataclasses import dataclass
import json
import os

commandList = []

TopFields = namedtuple('TopFields', ['pid','user','pr','ni','virt','res','shr', 's', 'cpu','mem','time','command'])

@dataclass
class Stats:
    cpu: int = 1
    memory: int = 1

    def get_value(self) -> float:
        return (self.cpu ** 2 + self.memory ** 2) ** 0.5


class CommandStats(dict):
    def __missing__(self, key):
        self[key] = self.factory(key)
        return self[key]

    def factory(self, key):
        return Stats(1, 1)


commands = CommandStats()


with open("top.out", "r") as topFile:
    topOutput = topFile.read().split("\n")[7:]

    for line in topOutput[:-1]:
        fields = TopFields(*re.sub(r'\s+', ' ', line).strip().split(' '))

        try:
            if fields.command.count("/") > 0:
                command = fields.command.split("/")[0]
            else:
                command = fields.command

            cpu = float(fields.cpu.replace(",", "."))
            mem = float(fields.mem.replace(",", "."))

            if command != "top":
                commandList.append((command, cpu, mem))
        except:
            pass


for command, cpu, mem in commandList:
  commands[command].cpu += cpu
  commands[command].memory += mem


resourceFrequency = {}

for command, stats in commands.items():
    resourceFrequency[command] = stats.get_value()

width, height = None, None
try:
    width, height = ((os.popen("xrandr | grep '*'").read()).split()[0]).split("x")
    width = int(width)
    height = int(height)
except:
    pass

configJSON = json.loads(open("config.json", "r").read())

if not width or not height:
    width = configJSON['resolution']['width']
    height = configJSON['resolution']['height']

wc = WordCloud(
    background_color=configJSON["wordcloud"]["background"],
    width=width - 2 * int(configJSON["wordcloud"]["margin"]),
    height=height - 2 * int(configJSON["wordcloud"]["margin"])
).generate_from_frequencies(resourceFrequency)

wc.to_file('wc.png')

wordcloud = Image.open("wc.png")
wallpaper = Image.new('RGB', (width, height), configJSON["wordcloud"]["background"])
wallpaper.paste(
    wordcloud,
    (
        configJSON["wordcloud"]["margin"],
        configJSON["wordcloud"]["margin"]
    )
)

wallpaper.save("wallpaper.png")
