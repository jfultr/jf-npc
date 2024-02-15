## JF-npc

jf-npc is a project to create non-player characters with complex speech behavior based on LLM.

## Installation
>Note: build tested on wsl Ubuntu 22.04

Install dependencies. Install setup tools before run poetry init
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install build-essential python3-dev gcc -y
```
Use the package manager [poetry](https://python-poetry.org/) to install jf-npc.

```bash
poetry init
```
## Usage

Before you can run the apps you shoud setup tokens. Just paste tokens to ***.env.example*** and rename it to ***.env***

This way, the apps can parse your tokens
### Apps:
* **telegram-agent**: app implements npc as a telegram chat-bot
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)