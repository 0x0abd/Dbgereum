# Dbgereum
Dbgereum is an EVM debugger for Ethereum smart contracts. It will help you to proceed with dynamic analysis on EVM bytecode.
You don't need to setup nodes and deploy transactions to the net. Just load bytecode and here you go. Nobody can trace your transactions/ideas and apply it on the mainnet.

Features:
* Change stack/memory/storage on-the-fly
* Use breakpoints
* Start analyze bytecode at any offset
* Save project and proceed later or share with others
* Modify environment variables such as call_value, call_data, timestamp, difficulty, etc...
* Make comments, enable/disable opcodes, proceed with searchbox

# Usage
You may start project just by doubleclick on DBGEREUM.py or with terminal command:
```
python DBGEREUM.py
```

**UI**  
![User Interface](/img/UI.png)
[1, 2]menu panel, [3]disassembly box, [4]stack box, [5]memory box, [6]storage box, [7, 8, 9]control buttons.

**file menu**
![View of the file menu](/img/file_menu.png)
Let me explain how to use any option here:
* _Open file(byte)_ - means that you have a __binary__ file with bytecode [x]
* _Open file(string)_ - means that you have a file with a string which correspond bytecode [x]
* _Open bytes_ - it's a dialogue box which asks you to input bytecode string to the field [x]
* _Open account(web)_  - just insert smart contract address and Dbgereum will parse it from etherscan.io. To use this option you need internet connection [x]
* _Open transaction(web)_ - just insert txn hash and Dbgereum will parse all neccessary data from etherscan.io. To use this option you need internet connection [xx]
* _Load Snapshot_ - you can load/import your saved project and continue your research
* _Save Snapshot_ - you can save/export your project for the next time

[x] - In that option Dbgereum will use [default] environment variables  
[xx] - In that option Dbgereum will use [mainnet] environment variables

**edit menu**
![View of the edit menu](/img/edit_menu.png)
Let me explain how to use any option here:
* _Override transaction_ - you can override transaction data(environment variables) at any offset of your bytecode research and this changes will be applied immediately
  - _Json file_ - specify a json file with data to be overrided. Example you can find in a project file __OVERRIDE_DATA__
  - _Json raw_ - dialogue box which will ask you to insert text with a data in json format
  - _Import from web by txn hash_ - just insert txn hash and Dbgereum will parse all neccessary data from etherscan.io. To use this option you need internet connection
* _View transaction_ - here you can view your current transaction data and change it
* _Save transaction_ - you can save transaction data to json file for the next usage
* _Opcodes on/off_ - You can turn on/off opcodes for instructions

**disassembly hotkeys**
![View of the edit menu](/img/disasm.png)
* [Ctrl+A/Cmd+A] - Select All
* [Ctrl+C/Cmd+C] - Copy
* [Ctrl+F/Cmd+F] - Search
* [F1] - Set/Change comment. Navigate cursor to the line and press F1
* [F2] - Set/Unset breakpoint
* [F4] - Change instruction pointer to any offset you need
* [F8] - Step. You could use button __Step__ instead
* [F9] - Run. You could use button __Run__ instead

**stack/memory/storage hotkeys**
![View of the edit menu](/img/stmemstor.png)
* [Ctrl+A/Cmd+A] - Select All
* [Ctrl+C/Cmd+C] - Copy
* [Ctrl+F/Cmd+F] - Search
* [F4] - Change stack/memory/storage. Navigate cursor to the line and press F4
* [F8] - Step. You could use button __Step__ instead. Refers to the disassembly box
* [F9] - Run. You could use button __Run__ instead. Refers to the disassembly box

# How it works
It has 2 classes:
* GUI - graphics
* Dbgereum - the main debugger logic

GUI is initiated in main function and it has 2 objects. It combines logic with graphics: Dbgereum and _tkinter_. _Tkinter_ it is a 3rd party library for work with graphics.

# How to install
The project has 4 dependencies: keccak hash function from __pycryptodome__, __requests__ for web, __json__ interactions and __tkinter__ for graphics. So you need:
```
pip3 install pycryptodome
pip3 install requests
```
And for mac osx and unix:
```
pip3 install tk
```
And for unix you will also need:
```
apt-get install python3-tk
```


# To-Do List
- [ ] Implement storage parsing
- [ ] Implement fuzzing functionality
- [ ] Implement call graph
- [ ] Cover opcodes emulation tests
- [ ] Track for etherscan.io changes

> Opcodes emulation is not tested and it's under maintenance.  
> Bug reports, issues, pull requests are welcome.  
> **IMPORTANT:** By submitting a patch, you agree to allow the project owner to license your work under the same license as that used by the project.
