# Blockies Identicons for ANSI Terminal

python port of https://github.com/ethereum/blockies

## Demo

[![asciicast](https://asciinema.org/a/Ps8rtHqL8z8Ur9xx5OP6MfIYO.png)](https://asciinema.org/a/Ps8rtHqL8z8Ur9xx5OP6MfIYO)

### Dependencies

- python3

### Installation
	
    pip install git+https://github.com/konradkonrad/blockies-py.git

### Usage

#### Commandline

    blockies 0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359

#### From python

```python
from blockies import create_blockie
rows = create_blockie('0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359')
# `rows` contains ansi escaped strings
for row in rows:
    print(row)
```
