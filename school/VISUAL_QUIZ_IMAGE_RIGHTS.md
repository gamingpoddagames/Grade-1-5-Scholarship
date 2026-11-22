# Sinhala picture-quiz image sources and licences

Each selected file is a **specific, manually reviewed Wikimedia Commons image**, not a search result chosen at posting time. The original photograph is cropped to fit 1080×1350 Facebook cards and 1080×1920 vertical quiz videos.

| Subject | File | Photographer / source | Licence |
|---|---|---|---|
| Sri Lankan leopard | [Sri Lankan leopard - Panthera pardus kotiya.jpg](https://commons.wikimedia.org/wiki/File:Sri_Lankan_leopard_-_Panthera_pardus_kotiya.jpg) | Senthi Aathavan Senthilverl | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Sri Lankan elephant | [ElephantSriLanka.jpg](https://commons.wikimedia.org/wiki/File:ElephantSriLanka.jpg) | Kvenkat07 | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Saturn | [Full Disk of Saturn.jpg](https://commons.wikimedia.org/wiki/File:Full_Disk_of_Saturn.jpg) | NASA Voyager 1 | US government public domain |
| Earth | [Apollo 17 Earth photograph](https://commons.wikimedia.org/wiki/File:The_Earth_seen_from_Apollo_17_(Original_Orientation).jpg) | NASA Apollo 17 | US government public domain |
| Blue morpho butterfly | [Blue morpho.jpg](https://commons.wikimedia.org/wiki/File:Blue_morpho.jpg) | Elsendor | Public domain |
| Green sea turtle | [Green Sea Turtle swimming.jpg](https://commons.wikimedia.org/wiki/File:Green_Sea_Turtle_swimming.jpg) | RobertoCostaPinto | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Bee-eaters | [Feeding Bee-eaters.jpg](https://commons.wikimedia.org/wiki/File:Feeding_Bee-eaters.jpg) | Chamara Ranathunga | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Sigiriya | [Sri Lanka-Sigiriya-Rock.JPG](https://commons.wikimedia.org/wiki/File:Sri_Lanka-Sigiriya-Rock.JPG) | Dschen Reinecke | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |

**Attribution and adaptations:** Credit the named photographer and Wikimedia Commons, link to the source and licence, and describe the crop and the additional quiz text. Composite artwork based on a CC BY-SA image should be redistributed under the corresponding CC BY-SA licence. These links provide the full attribution detail missing from character-limited social captions. Brand identifiers and other independently owned rights are not licensed merely by this document.

The renderer fails closed if the approved photo is unavailable, its file has moved, or an untrusted host is returned. **Do not substitute an unrelated stock image**: fix the named source or supply a new verified, correctly licensed photo.

## Editorial strategy

- Picture-first wildlife, nature, space, ocean and Sri Lankan heritage for Grade 1–5 audiences
- 8 different images, each with 2 independently checked questions (16 unique daily question texts before cycling)
- Facebook photo **does not reveal** the answer; video reveals the correct answer after thinking time
- Same Asia/Colombo date selects the same photo and question for both formats
- Existing mathematics/PDF resources are unchanged

Run offline bank tests:

```sh
python -m unittest discover -s school -p test_visual_quiz.py -v
```

Image download is deliberately a separate live requirement and needs a GitHub Actions execution with outbound access to Wikimedia.
