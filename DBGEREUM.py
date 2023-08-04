#!/usr/bin/env python3
# The project is written in Python 3.8.3 #
import requests, json
from Crypto.Hash import keccak
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from pathlib import Path
from platform import system

#######################################CURRENT_PATH########################################
location = str(Path(__file__).absolute().parent) + "/"
###########################################################################################

#########################################PLATFORM##########################################
platform = system().lower()
platform_font = {"windows":("Monaco", 9), "linux":("Terminal", 9), "darwin":("Monaco", 12)}
platfrom_width = {"windows":71, "linux":63, "darwin":55}
###########################################################################################

#######################################Etherscan.io########################################
TOKEN = ""
with open(location + "TOKEN.dat", "r") as f:
    TOKEN = f.read()[:34]
###########################################################################################

_table = {#opcode: (name, immediate_operand_size, pops, pushes, gas, description)
                # https://ethervm.io/

                0x00: ('STOP', 0, 0, 0, 0, 'Halts execution.'),
                0x01: ('ADD', 0, 2, 1, 3, 'Addition operation.'),
                0x02: ('MUL', 0, 2, 1, 5, 'Multiplication operation.'),
                0x03: ('SUB', 0, 2, 1, 3, 'Subtraction operation.'),
                0x04: ('DIV', 0, 2, 1, 5, 'Integer division operation.'),
                0x05: ('SDIV', 0, 2, 1, 5, 'Signed integer division operation (truncated).'),
                0x06: ('MOD', 0, 2, 1, 5, 'Modulo remainder operation.'),
                0x07: ('SMOD', 0, 2, 1, 5, 'Signed modulo remainder operation.'),
                0x08: ('ADDMOD', 0, 3, 1, 8, 'Modulo addition operation.'),
                0x09: ('MULMOD', 0, 3, 1, 8, 'Modulo multiplication operation.'),
                0x0a: ('EXP', 0, 2, 1, 10, 'Exponential operation.'),
                0x0b: ('SIGNEXTEND', 0, 2, 1, 5, "Extend length of two's complement signed integer."),
                0x10: ('LT', 0, 2, 1, 3, 'Less-than comparision.'),
                0x11: ('GT', 0, 2, 1, 3, 'Greater-than comparision.'),
                0x12: ('SLT', 0, 2, 1, 3, 'Signed less-than comparision.'),
                0x13: ('SGT', 0, 2, 1, 3, 'Signed greater-than comparision.'),
                0x14: ('EQ', 0, 2, 1, 3, 'Equality comparision.'),
                0x15: ('ISZERO', 0, 1, 1, 3, 'Simple not operator.'),
                0x16: ('AND', 0, 2, 1, 3, 'Bitwise AND operation.'),
                0x17: ('OR', 0, 2, 1, 3, 'Bitwise OR operation.'),
                0x18: ('XOR', 0, 2, 1, 3, 'Bitwise XOR operation.'),
                0x19: ('NOT', 0, 1, 1, 3, 'Bitwise NOT operation.'),
                0x1a: ('BYTE', 0, 2, 1, 3, 'Retrieve single byte from word.'),
                0x1b: ('SHL', 0, 2, 1, 3, 'Logical Shift left.'), #changed
                0x1c: ('SHR', 0, 2, 1, 3, 'Logical Shift right.'), #changed
                0x1d: ('SAR', 0, 2, 1, 3, 'Arithmetic shift right.'), #changed
                0x20: ('SHA3', 0, 2, 1, 30, 'Compute Keccak-256 hash.'),
                0x30: ('ADDRESS', 0, 0, 1, 2, 'Get address of currently executing account.'),
                0x31: ('BALANCE', 0, 1, 1, 20, 'Get balance of the given account.'),
                0x32: ('ORIGIN', 0, 0, 1, 2, 'Get execution origination address.'),
                0x33: ('CALLER', 0, 0, 1, 2, 'Get caller address.'),
                0x34: ('CALLVALUE', 0, 0, 1, 2, 'Get deposited value by the instruction/transaction responsible for this execution.'),
                0x35: ('CALLDATALOAD', 0, 1, 1, 3, 'Get input data of current environment.'),
                0x36: ('CALLDATASIZE', 0, 0, 1, 2, 'Get size of input data in current environment.'),
                0x37: ('CALLDATACOPY', 0, 3, 0, 3, 'Copy input data in current environment to memory.'),
                0x38: ('CODESIZE', 0, 0, 1, 2, 'Get size of code running in current environment.'),
                0x39: ('CODECOPY', 0, 3, 0, 3, 'Copy code running in current environment to memory.'),
                0x3a: ('GASPRICE', 0, 0, 1, 2, 'Get price of gas in current environment.'),
                0x3b: ('EXTCODESIZE', 0, 1, 1, 20, "Get size of an account's code."),
                0x3c: ('EXTCODECOPY', 0, 4, 0, 20, "Copy an account's code to memory."),
                0x3d: ('RETURNDATASIZE', 0, 0, 1, 2, "Pushes the size of the return data buffer onto the stack."), #changed
                0x3e: ('RETURNDATACOPY', 0, 3, 0, 3, "Copies data from the return data buffer."), #changed
                0x3f: ('EXTCODEHASH', 0, 1, 1, 700, "Get hash of the contract bytecode at addr."), #changed
                0x40: ('BLOCKHASH', 0, 1, 1, 20, 'Get the hash of one of the 256 most recent complete blocks.'),
                0x41: ('COINBASE', 0, 0, 1, 2, "Get the block's beneficiary address."),
                0x42: ('TIMESTAMP', 0, 0, 1, 2, "Get the block's timestamp."),
                0x43: ('NUMBER', 0, 0, 1, 2, "Get the block's number."),
                0x44: ('DIFFICULTY', 0, 0, 1, 2, "Get the block's difficulty."),
                0x45: ('GASLIMIT', 0, 0, 1, 2, "Get the block's gas limit."),
                0x46: ('CHAINID', 0, 0, 1, 2, "Get current network's chain id."), #changed EIP-1344
                0x47: ('SELFBALANCE', 0, 0, 1, 5, "Get balance of the executing contract in wei."), #changed EIP-1884
                0x48: ('BASEFEE', 0, 0, 1, 2, "Get current block's base fee."), #changed EIP-3198
                0x50: ('POP', 0, 1, 0, 2, 'Remove item from stack.'),
                0x51: ('MLOAD', 0, 1, 1, 3, 'Load word from memory.'),
                0x52: ('MSTORE', 0, 2, 0, 3, 'Save word to memory.'),
                0x53: ('MSTORE8', 0, 2, 0, 3, 'Save byte to memory.'),
                0x54: ('SLOAD', 0, 1, 1, 50, 'Load word from storage.'),
                0x55: ('SSTORE', 0, 2, 0, 0, 'Save word to storage.'),
                0x56: ('JUMP', 0, 1, 0, 8, 'Alter the program counter.'),
                0x57: ('JUMPI', 0, 2, 0, 10, 'Conditionally alter the program counter.'),
                0x58: ('GETPC', 0, 0, 1, 2, 'Get the value of the program counter prior to the increment.'),
                0x59: ('MSIZE', 0, 0, 1, 2, 'Get the size of active memory in bytes.'),
                0x5a: ('GAS', 0, 0, 1, 2, 'Get the amount of available gas, including the corresponding reduction the amount of available gas.'),
                0x5b: ('JUMPDEST', 0, 0, 0, 1, 'Mark a valid destination for jumps.'),
                0x60: ('PUSH', 1, 0, 1, 0, 'Place 1 byte item on stack.'),
                0x61: ('PUSH', 2, 0, 1, 0, 'Place 2-byte item on stack.'),
                0x62: ('PUSH', 3, 0, 1, 0, 'Place 3-byte item on stack.'),
                0x63: ('PUSH', 4, 0, 1, 0, 'Place 4-byte item on stack.'),
                0x64: ('PUSH', 5, 0, 1, 0, 'Place 5-byte item on stack.'),
                0x65: ('PUSH', 6, 0, 1, 0, 'Place 6-byte item on stack.'),
                0x66: ('PUSH', 7, 0, 1, 0, 'Place 7-byte item on stack.'),
                0x67: ('PUSH', 8, 0, 1, 0, 'Place 8-byte item on stack.'),
                0x68: ('PUSH', 9, 0, 1, 0, 'Place 9-byte item on stack.'),
                0x69: ('PUSH', 10, 0, 1, 0, 'Place 10-byte item on stack.'),
                0x6a: ('PUSH', 11, 0, 1, 0, 'Place 11-byte item on stack.'),
                0x6b: ('PUSH', 12, 0, 1, 0, 'Place 12-byte item on stack.'),
                0x6c: ('PUSH', 13, 0, 1, 0, 'Place 13-byte item on stack.'),
                0x6d: ('PUSH', 14, 0, 1, 0, 'Place 14-byte item on stack.'),
                0x6e: ('PUSH', 15, 0, 1, 0, 'Place 15-byte item on stack.'),
                0x6f: ('PUSH', 16, 0, 1, 0, 'Place 16-byte item on stack.'),
                0x70: ('PUSH', 17, 0, 1, 0, 'Place 17-byte item on stack.'),
                0x71: ('PUSH', 18, 0, 1, 0, 'Place 18-byte item on stack.'),
                0x72: ('PUSH', 19, 0, 1, 0, 'Place 19-byte item on stack.'),
                0x73: ('PUSH', 20, 0, 1, 0, 'Place 20-byte item on stack.'),
                0x74: ('PUSH', 21, 0, 1, 0, 'Place 21-byte item on stack.'),
                0x75: ('PUSH', 22, 0, 1, 0, 'Place 22-byte item on stack.'),
                0x76: ('PUSH', 23, 0, 1, 0, 'Place 23-byte item on stack.'),
                0x77: ('PUSH', 24, 0, 1, 0, 'Place 24-byte item on stack.'),
                0x78: ('PUSH', 25, 0, 1, 0, 'Place 25-byte item on stack.'),
                0x79: ('PUSH', 26, 0, 1, 0, 'Place 26-byte item on stack.'),
                0x7a: ('PUSH', 27, 0, 1, 0, 'Place 27-byte item on stack.'),
                0x7b: ('PUSH', 28, 0, 1, 0, 'Place 28-byte item on stack.'),
                0x7c: ('PUSH', 29, 0, 1, 0, 'Place 29-byte item on stack.'),
                0x7d: ('PUSH', 30, 0, 1, 0, 'Place 30-byte item on stack.'),
                0x7e: ('PUSH', 31, 0, 1, 0, 'Place 31-byte item on stack.'),
                0x7f: ('PUSH', 32, 0, 1, 0, 'Place 32-byte (full word) item on stack.'),
                0x80: ('DUP', 0, 1, 2, 3, 'Duplicate 1st stack item.'),
                0x81: ('DUP', 0, 2, 3, 3, 'Duplicate 2nd stack item.'),
                0x82: ('DUP', 0, 3, 4, 3, 'Duplicate 3rd stack item.'),
                0x83: ('DUP', 0, 4, 5, 3, 'Duplicate 4th stack item.'),
                0x84: ('DUP', 0, 5, 6, 3, 'Duplicate 5th stack item.'),
                0x85: ('DUP', 0, 6, 7, 3, 'Duplicate 6th stack item.'),
                0x86: ('DUP', 0, 7, 8, 3, 'Duplicate 7th stack item.'),
                0x87: ('DUP', 0, 8, 9, 3, 'Duplicate 8th stack item.'),
                0x88: ('DUP', 0, 9, 10, 3, 'Duplicate 9th stack item.'),
                0x89: ('DUP', 0, 10, 11, 3, 'Duplicate 10th stack item.'),
                0x8a: ('DUP', 0, 11, 12, 3, 'Duplicate 11th stack item.'),
                0x8b: ('DUP', 0, 12, 13, 3, 'Duplicate 12th stack item.'),
                0x8c: ('DUP', 0, 13, 14, 3, 'Duplicate 13th stack item.'),
                0x8d: ('DUP', 0, 14, 15, 3, 'Duplicate 14th stack item.'),
                0x8e: ('DUP', 0, 15, 16, 3, 'Duplicate 15th stack item.'),
                0x8f: ('DUP', 0, 16, 17, 3, 'Duplicate 16th stack item.'),
                0x90: ('SWAP', 0, 2, 2, 3, 'Exchange 1st and 2nd stack items.'),
                0x91: ('SWAP', 0, 3, 3, 3, 'Exchange 1st and 3rd stack items.'),
                0x92: ('SWAP', 0, 4, 4, 3, 'Exchange 1st and 4th stack items.'),
                0x93: ('SWAP', 0, 5, 5, 3, 'Exchange 1st and 5th stack items.'),
                0x94: ('SWAP', 0, 6, 6, 3, 'Exchange 1st and 6th stack items.'),
                0x95: ('SWAP', 0, 7, 7, 3, 'Exchange 1st and 7th stack items.'),
                0x96: ('SWAP', 0, 8, 8, 3, 'Exchange 1st and 8th stack items.'),
                0x97: ('SWAP', 0, 9, 9, 3, 'Exchange 1st and 9th stack items.'),
                0x98: ('SWAP', 0, 10, 10, 3, 'Exchange 1st and 10th stack items.'),
                0x99: ('SWAP', 0, 11, 11, 3, 'Exchange 1st and 11th stack items.'),
                0x9a: ('SWAP', 0, 12, 12, 3, 'Exchange 1st and 12th stack items.'),
                0x9b: ('SWAP', 0, 13, 13, 3, 'Exchange 1st and 13th stack items.'),
                0x9c: ('SWAP', 0, 14, 14, 3, 'Exchange 1st and 14th stack items.'),
                0x9d: ('SWAP', 0, 15, 15, 3, 'Exchange 1st and 15th stack items.'),
                0x9e: ('SWAP', 0, 16, 16, 3, 'Exchange 1st and 16th stack items.'),
                0x9f: ('SWAP', 0, 17, 17, 3, 'Exchange 1st and 17th stack items.'),
                0xa0: ('LOG', 0, 2, 0, 375, 'Append log record with no topics.'),
                0xa1: ('LOG', 0, 3, 0, 750, 'Append log record with one topic.'),
                0xa2: ('LOG', 0, 4, 0, 1125, 'Append log record with two topics.'),
                0xa3: ('LOG', 0, 5, 0, 1500, 'Append log record with three topics.'),
                0xa4: ('LOG', 0, 6, 0, 1875, 'Append log record with four topics.'),
                0xf0: ('CREATE', 0, 3, 1, 32000, 'Create a new account with associated code.'),
                0xf1: ('CALL', 0, 7, 1, 40, 'Message-call into an account.'),
                0xf2: ('CALLCODE', 0, 7, 1, 40, "Message-call into this account with alternative account's code."),
                0xf3: ('RETURN', 0, 2, 0, 0, 'Halt execution returning output data.'),
                0xf4: ('DELEGATECALL', 0, 6, 1, 40, "Message-call into this account with an alternative account's code, but persisting into this account with an alternative account's code."),
                0xf5: ('BREAKPOINT', 0, 0, 0, 40, 'Not in yellow paper FIXME'),
                0xf6: ('RNGSEED', 0, 1, 1, 0, 'Not in yellow paper FIXME'),
                0xf7: ('SSIZEEXT', 0, 2, 1, 0, 'Not in yellow paper FIXME'),
                0xf8: ('SLOADBYTES', 0, 3, 0, 0, 'Not in yellow paper FIXME'),
                0xf9: ('SSTOREBYTES', 0, 3, 0, 0, 'Not in yellow paper FIXME'),
                0xfa: ('SSIZE', 0, 1, 1, 40, 'Not in yellow paper FIXME'),
                0xfb: ('STATEROOT', 0, 1, 1, 0, 'Not in yellow paper FIXME'),
                0xfc: ('TXEXECGAS', 0, 0, 1, 0, 'Not in yellow paper FIXME'),
                0xfd: ('REVERT', 0, 2, 0, 0, 'Stop execution and revert state changes, without consuming all provided gas and providing a reason.'),
                0xfe: ('INVALID', 0, 0, 0, 0, 'Designated invalid instruction.'),
                0xff: ('SELFDESTRUCT', 0, 1, 0, 5000, 'Halt execution and register account for later deletion.')
            }


##############################################################################################################
#            Gui draw and logic with it such as redraw, identification, commands and hotkeys etc...          #
##############################################################################################################

class GUI:
    def __init__(self):

        #######################################################
        ####                 INIT_DBGEREUM                 ####
        #######################################################

        self.Dbgereum = Dbgereum()
        
        #######################################################
        ####                 INIT_TKINTER                  ####
        #######################################################

        win = Tk()
        win.title("Dbgereum")
        
        #######################################################
        ####                    WINDOW                     ####
        #######################################################

        dis_text = Text(win, width = 155,height = 30, highlightthickness = 0, borderwidth = 0, background="black", foreground="white", insertbackground = "white")
        stack_text = Text(win, width = platfrom_width[platform], height = 10, highlightthickness = 1, borderwidth = 0, background="black", foreground="white", highlightcolor= "red", highlightbackground = "gray", insertbackground = "white")
        memory_text = Text(win, width = platfrom_width[platform], height = 10, highlightthickness = 1, borderwidth = 0, background="black", foreground="white", highlightcolor= "red", highlightbackground = "gray", insertbackground = "white")
        storage_text = Text(win, width = platfrom_width[platform], height = 10, highlightthickness = 1, borderwidth = 0, background="black", foreground="white", highlightcolor= "red", highlightbackground = "gray", insertbackground = "white")
        label1 = Label(win, width = platfrom_width[platform], bg = "black", fg = "white", highlightthickness = 0, text = "STACK")
        label2 = Label(win, width = platfrom_width[platform], bg = "black", fg = "white", highlightthickness = 0, text = "MEMORY")
        label3 = Label(win, width = platfrom_width[platform], bg = "black", fg = "white", highlightthickness = 0, text = "STORAGE")
        label4 = Label(win, width = platfrom_width[platform], bg = "black", fg = "white", highlightthickness = 0, text = "")
        dis_text.configure(font = platform_font[platform])
        stack_text.configure(font = platform_font[platform])
        memory_text.configure(font = platform_font[platform])
        storage_text.configure(font = platform_font[platform])
        scroll1 = Scrollbar(command = dis_text.yview)
        b1 = Button(win, text = "STEP", activeforeground = "magenta", highlightbackground = "black", command = lambda: self.Step(dis_text, stack_text, memory_text, storage_text))
        b2 = Button(win, text = "RUN", activeforeground = "magenta", highlightbackground = "black", command = lambda: self.Run(dis_text, stack_text, memory_text, storage_text))
        b3 = Button(win, text = "RESTART", activeforeground = "magenta", highlightbackground = "black", command = lambda: self.Restart(dis_text, stack_text, memory_text, storage_text))

        win.bind("<Key>", lambda e: self.keyProcessingMain(e, dis_text, stack_text, memory_text, storage_text))
        dis_text.bind("<Key>", lambda e: self.keyProcessing(e, win, dis_text, stack_text, memory_text, storage_text))
        scroll1.pack(side=RIGHT, fill=Y)
        stack_text.bind("<Key>", lambda e: self.keyProcessingStack(e, win, dis_text, stack_text, memory_text, storage_text))
        memory_text.bind("<Key>", lambda e: self.keyProcessingMemory(e, win, dis_text, stack_text, memory_text, storage_text))
        storage_text.bind("<Key>", lambda e: self.keyProcessingStorage(e, win, dis_text, stack_text, memory_text, storage_text))

        dis_text.configure(yscrollcommand=scroll1.set)
        dis_text.pack(side = LEFT, expand=True, fill='both')
        label1.pack(side = TOP, expand=True, fill='both')
        stack_text.pack(side = TOP, expand=True, fill='both')
        label2.pack(side = TOP, expand=True, fill='both')
        memory_text.pack(side = TOP, expand=True, fill='both')
        label3.pack(side = TOP, expand=True, fill='both')
        storage_text.pack(side = TOP, expand=True, fill='both')
        label4.pack(side = TOP, expand=True, fill='both')
        b1.pack(side = LEFT, expand=True, fill='both')
        b2.pack(side = LEFT, expand=True, fill='both')
        b3.pack(side = LEFT, expand=True, fill='both')

        #######################################################
        ####                      MENU                     ####
        #######################################################

        mainmenu = Menu(win)
        win.config(menu=mainmenu)
        
        filemenu = Menu(mainmenu, tearoff=0)
        filemenu.add_command(label = "Open file(byte)", command = lambda: self.onOpenFileByte(dis_text, stack_text, memory_text, storage_text))
        filemenu.add_command(label = "Open file(string)", command = lambda: self.onOpenFileString(dis_text, stack_text, memory_text, storage_text))
        filemenu.add_command(label = "Open bytes", command = lambda: self.onOpenBytes(win, dis_text, stack_text, memory_text, storage_text))
        filemenu.add_command(label = "Open account(web)", command = lambda: self.onOpenAccount(win, dis_text, stack_text, memory_text, storage_text))
        filemenu.add_command(label = "Open transaction(web)", command = lambda: self.onOpenTransaction(win, dis_text, stack_text, memory_text, storage_text))
        filemenu.add_separator()
        filemenu.add_command(label = "Load Snapshot", command = lambda: self.onLoad(dis_text, stack_text, memory_text, storage_text))
        filemenu.add_command(label = "Save Snapshot", command = self.onSave)
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command = win.quit)
        mainmenu.add_cascade(label = "File", menu = filemenu)
        
        filemenu2 = Menu(mainmenu, tearoff=0)
        submenu = Menu(mainmenu, tearoff=0)
        submenu.add_command(label = "Json file", command = self.onOverAsFile)
        submenu.add_command(label = "Json raw", command = lambda: self.onOverAsRaw(win))
        submenu.add_separator()
        submenu.add_command(label = "Import from web by txn hash", command = lambda: self.onWebImport(win))
        filemenu2.add_cascade(label = "Override transaction", menu = submenu)
        filemenu2.add_command(label = "View transaction", command = self.onViewTransaction)
        filemenu2.add_command(label = "Save transaction", command = self.onSaveTransaction)
        filemenu2.add_separator()
        filemenu2.add_command(label = "Opcodes on/off", command = lambda: self.onOpcodes(dis_text))
        mainmenu.add_cascade(label = "Edit", menu = filemenu2)
        
        win.mainloop()

    def createMenu(self, root, dis_text, stack_text, memory_text, storage_text):
        return
    
    def onViewTransaction(self):
        txn = Tk()
        txn.title("Transaction")

        txt = [None] * 16
        lbl = [None] * 16
        ind = ["this_address", "this_balance", "tx_origin", "tx_gasprice", "blockhash", "block_coinbase", "block_timestamp", "block_number", "block_difficulty", "block_gaslimit", "chain_id", "base_fee", "msg_caller", "msg_value", "msg_data"]
        names = ["ADDRESS", "BALANCE", "TX_ORIGIN", "TX_GASPRICE", "BLOCKHASH", "BLOCK_COINBASE", "BLOCK_TIMESTAMP", "BLOCK_NUMBER", "BLOCK_DIFFICULTY", "BLOCK_GASLIMIT", "CHAIN_ID", "BASE_FEE", "MSG_CALLER", "MSG_VALUE", "MSG_DATA"]

        txn.columnconfigure(0, pad = 3)
        txn.columnconfigure(1, pad = 3)
        txn.configure(background = "black")

        for i in range(0, 15):
            txt[i] = Entry(txn, width = 64, highlightthickness = 1, background = "black", foreground = "white", highlightcolor = "red", highlightbackground = "gray", insertbackground = "white")
            txt[i].configure(font = platform_font[platform])
            lbl[i] = Label(txn, bg = "black", fg = "white", text = names[i])
            txn.rowconfigure(i, pad = 3)

            lbl[i].grid(row = i, column = 0)
            txt[i].grid(row = i, column = 1, stick = W + E)
        
        def printTransaction(data):
            if data == "":
                return
            for i in range(0, 15):
                txt[i].insert(END, data[ind[i]])

        def onSaveTransaction():
            dat = "{\"this_address\":\"" + txt[0].get() + "\",\"this_balance\":\"" + txt[1].get() + "\",\"tx_origin\":\"" + txt[2].get() + "\",\"tx_gasprice\":\"" + txt[3].get() + "\",\"blockhash\":\"" + txt[4].get() + "\",\"block_coinbase\":\"" + txt[5].get() + "\",\"block_timestamp\":\"" + txt[6].get() + "\",\"block_number\":\"" + txt[7].get() + "\",\"block_difficulty\":\"" + txt[8].get() + "\",\"block_gaslimit\":\"" + txt[9].get() + "\",\"chain_id\":\"" + txt[10].get() + "\",\"base_fee\":\"" + txt[11].get() + "\",\"msg_caller\":\"" + txt[12].get() + "\",\"msg_value\":\"" + txt[13].get() + "\",\"msg_data\":\"" + txt[14].get() + "\"}"
            res = self.Dbgereum.verify_offline_data(json.loads(dat))
            if res == 0:
                messagebox.showwarning(title = "Error", message = "Incorrect format")
            else:
                "saved"
                self.Dbgereum.data = json.loads(dat)
                txn.destroy()

        btn1 = Button(txn, text = "Save", activeforeground = "magenta", highlightbackground = "black", command = onSaveTransaction)
        btn1.grid(row = 16, column = 1, sticky = W + E)

        printTransaction(self.Dbgereum.data)

        txn.mainloop()

    def onSaveTransaction(self):
        try:
            fname = filedialog.asksaveasfilename(title = "Save as", filetypes = (("Txn data .dat ","*.*"),("All files","*.*")))
            if fname == "":
                return
            
            with open(fname + ".dat", 'w') as f:
                f.write(json.dumps(self.Dbgereum.data))
            
            messagebox.showinfo(title = "Done", message = "Transaction data has successfully saved")

        except:
            nothing = 0

    def onOpenAccount(self, root, dis_text, stack_text, memory_text, storage_text):
        try:
            account = simpledialog.askstring("Smart Contract Account", "Input Account:", parent = root)
            if account[0:2] != "0x":
                account = "0x" + account
            if len(account) != 42:
                messagebox.showwarning(title = "Warning", message = "Invalid account!")
                return

            r3 = requests.get('https://etherscan.io/address/' + account, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})
            i = r3.text.find('verifiedbytecode2') + 19
            k = r3.text[i:].find('<')
            self.Dbgereum.bytecode = bytes.fromhex(r3.text[i:i + k])
            self.Dbgereum.flushObject()
            self.Dbgereum.getLastOffset()
            self.Dbgereum.init_memory()
            self.Dbgereum.init_storage()
            self.disassemble(dis_text)
            self.printStack(stack_text)
            self.printMemory(memory_text)
            self.printStorage(storage_text)
            self.initOverData()
        except:
            nothing = 0
    
    def onOpenTransaction(self, root, dis_text, stack_text, memory_text, storage_text):
        try:
            txn = simpledialog.askstring("Transaction Hash", "txn:", parent = root)
            if txn == None:
                return
            dat = self.Dbgereum.parse_online_data(txn, 1)
            if dat != "0":
                self.Dbgereum.data = dat
                messagebox.showerror(title = "Done", message = "The data has successfully loaded")
            else:
                messagebox.showwarning(title = "Error", message = "Hash invalid or connectivity issue")
                return
            self.Dbgereum.flushObject()
            self.Dbgereum.getLastOffset()
            self.Dbgereum.init_memory()
            self.Dbgereum.init_storage()
            self.disassemble(dis_text)
            self.printStack(stack_text)
            self.printMemory(memory_text)
            self.printStorage(storage_text)
        except:
            nothing = 0

    def onOpenFileByte(self, dis_text, stack_text, memory_text, storage_text):
        try:
            fname = filedialog.askopenfilename(title = "Open file", filetypes = (("EVM bytecode .byte ","*.*"), ("All files","*.*")))
            with open(fname, 'rb') as fd:
                self.Dbgereum.bytecode = fd.read()
            self.Dbgereum.flushObject()
            self.Dbgereum.getLastOffset()
            self.Dbgereum.init_memory()
            self.Dbgereum.init_storage()
            self.disassemble(dis_text)
            self.printStack(stack_text)
            self.printMemory(memory_text)
            self.printStorage(storage_text)
            self.initOverData()
        except:
            nothing = 0
    
    def onOpenFileString(self, dis_text, stack_text, memory_text, storage_text):
        try:
            fname = filedialog.askopenfilename(title = "Open file", filetypes = (("EVM bytecode .txt ","*.*"), ("All files","*.*")))
            with open(fname, 'r') as fd:
                self.Dbgereum.bytecode = bytes.fromhex(fd.read())
            self.Dbgereum.flushObject()
            self.Dbgereum.getLastOffset()
            self.Dbgereum.init_memory()
            self.Dbgereum.init_storage()
            self.disassemble(dis_text)
            self.printStack(stack_text)
            self.printMemory(memory_text)
            self.printStorage(storage_text)
            self.initOverData()
        except:
            nothing = 0

    def onOpenBytes(self, root, dis_text, stack_text, memory_text, storage_text):
        try:
            try:
                value = simpledialog.askstring("Bytecode", "Input Bytecode:", parent = root)
                if value == None:
                    return
                self.Dbgereum.bytecode = bytes.fromhex(value)
            except:
                messagebox.showwarning(title = "Warning", message = "Format incorrect")
                return
            self.Dbgereum.flushObject()
            self.Dbgereum.getLastOffset()
            self.Dbgereum.init_memory()
            self.Dbgereum.init_storage()
            self.disassemble(dis_text)
            self.printStack(stack_text)
            self.printMemory(memory_text)
            self.printStorage(storage_text)
            self.initOverData()
        except:
            nothing = 0

    def onLoad(self, dis_text, stack_text, memory_text, storage_text):
        try:
            self.Dbgereum.flushObject()
            fname = filedialog.askopenfilename(title = "Open file", filetypes = (("Dbgereum .evm ","*.*"), ("All files","*.*")))
            if fname == "":
                return
            with open(fname, 'rb') as f:
                data = f.read()
            
            i = data.find(b'\x0a\xbd')
            self.Dbgereum.bytecode = data[:i]
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            comments = data[:i]
            for k in range(0, comments.count(b"\xbd") // 2):
                offset = int(comments[:comments.find(b'\xbd')].decode("utf-8"))
                comments = comments[comments.find(b'\xbd') + 1:]
                value = comments[:comments.find(b'\xbd')].decode("utf-8")
                comments = comments[comments.find(b'\xbd') + 1:]
                self.Dbgereum.comments.update({offset:value})
            data = data[i + 2:]
            
            i = data.find(b'\x0a\xbd')
            self.Dbgereum.ip = int(data[:i].decode("utf-8"))
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            self.Dbgereum.line = int(data[:i].decode("utf-8"))
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            self.Dbgereum.last_instruction = int(data[:i].decode("utf-8"))
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            breakpoints = data[:i]
            for k in range(0, breakpoints.count(b"\xbd") // 2):
                offset = str(breakpoints[:breakpoints.find(b'\xbd')].decode("utf-8"))
                breakpoints = breakpoints[breakpoints.find(b'\xbd') + 1:]
                value = breakpoints[:breakpoints.find(b'\xbd')].decode("utf-8")
                breakpoints = breakpoints[breakpoints.find(b'\xbd') + 1:]
                self.Dbgereum.breakpoints.update({offset:value})
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            stack = data[:i]
            for k in range(0, stack.count(b"\xbd")):
                value = stack[:stack.find(b'\xbd')].decode("utf-8")
                self.Dbgereum.stack.append(value)
                stack = stack[stack.find(b'\xbd') + 1:]
            data = data[i + 2:]

            self.Dbgereum.init_memory()
            i = data.find(b'\x0a\xbd')
            memory = data[:i]
            for k in range(0, memory.count(b"\xbd") // 2):
                offset = int(memory[:memory.find(b'\xbd')].decode("utf-8"))
                memory = memory[memory.find(b'\xbd') + 1:]
                value = str(memory[:memory.find(b'\xbd')].decode("utf-8"))
                memory = memory[memory.find(b'\xbd') + 1:]
                s = 0
                for n in range(0, 32):
                    self.Dbgereum.memory[offset * 32 + n] = value[s:s + 2]
                    s += 2
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            self.Dbgereum.memory_size = int(data[:i].decode("utf-8"))
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            storage = data[:i]
            for k in range(0, storage.count(b"\xbd")):
                value = str(storage[:storage.find(b'\xbd')].decode("utf-8"))
                self.Dbgereum.storage.append(value)
                storage = storage[storage.find(b'\xbd') + 1:]
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            self.Dbgereum.gas_remaining = int(data[:i].decode("utf-8"))
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            self.Dbgereum.opcodes = int(data[:i].decode("utf-8"))
            data = data[i + 2:]

            i = data.find(b'\x0a\xbd')
            self.Dbgereum.data = json.loads(data[:i].decode("utf-8").replace("'", '"'))
            data = data[i + 2:]
            
            self.disassemble(dis_text)
            self.printStack(stack_text)
            self.printMemory(memory_text)
            self.printStorage(storage_text)

        except:
            nothing = 0
    
    def onSave(self):
        try:
            fname = filedialog.asksaveasfilename(title = "Save as", filetypes = (("Dbgereum .evm ","*.*"),("All files","*.*")))
            if fname == "":
                return
            comments = b""
            breakpoints = b""
            stack = b""
            memory = b""
            storage = b""

            for i in self.Dbgereum.comments.items():
                comments += bytes(str(i[0]), "utf-8") + b"\xbd" + bytes(i[1], "utf-8") + b"\xbd"

            for i in self.Dbgereum.breakpoints.items():
                breakpoints += bytes(str(i[0]), "utf-8") + b"\xbd" + bytes(str(i[1]), "utf-8") + b"\xbd"

            for i in range(0, len(self.Dbgereum.stack)):
                stack += bytes(self.Dbgereum.stack[i], "utf-8") + b"\xbd"
            
            k = 0
            tmp = ""
            for i in range(0, len(self.Dbgereum.memory)):
                if i % 32 == 0 and i != 0:
                    if int(tmp, 16) != 0:
                        memory += bytes(str(k), "utf-8") + b"\xbd" + bytes(tmp, "utf-8") + b"\xbd"
                    k += 1
                    tmp = ""
                tmp += self.Dbgereum.memory[i]
            
            for i in range(0, len(self.Dbgereum.storage)):
                storage += bytes(self.Dbgereum.storage[i], "utf-8") + b"\xbd"

            data = self.Dbgereum.bytecode + b"\x0a\xbd" + comments + b"\x0a\xbd" + bytes(str(self.Dbgereum.ip), "utf-8") + b"\x0a\xbd" + bytes(str(self.Dbgereum.line), "utf-8") + b"\x0a\xbd" + bytes(str(self.Dbgereum.last_instruction), "utf-8") + b"\x0a\xbd" + breakpoints + b"\x0a\xbd" + stack + b"\x0a\xbd" + memory + b"\x0a\xbd" + bytes(str(self.Dbgereum.memory_size), "utf-8") + b"\x0a\xbd" + storage + b"\x0a\xbd" + bytes(str(self.Dbgereum.gas_remaining), "utf-8") + b"\x0a\xbd" + bytes(str(self.Dbgereum.opcodes), "utf-8") + b"\x0a\xbd" + bytes(str(self.Dbgereum.data), "utf-8") + b"\x0a\xbd"
            with open(fname + ".evm", 'wb') as f:
                f.write(data)
            
            messagebox.showinfo(title = "Done", message = "Snapshot has successfully saved")
        except:
            nothing = 0

    def initOverData(self):
        try:
            fname = location + "OVERRIDE_DATA.dat"
            with open(fname, 'r') as fd:
                dat = json.load(fd)
            res = self.Dbgereum.verify_offline_data(dat)
            if res != 0:
                self.Dbgereum.data = dat
                messagebox.showinfo(title = "Done", message = "The data has successfully loaded")
            else:
                messagebox.showwarning(title = "Warning", message = "Please, override transaction! Format incorrect")
        except:
            nothing = 0
            messagebox.showwarning(title = "Warning", message = "Please, override transaction! Go to: Edit->Override txn->...")

    def onOverAsFile(self):
        try:
            fname = filedialog.askopenfilename(title = "Open file", filetypes = (("Txn data ","*.*"), ("All files","*.*")))
            with open(fname, 'r') as fd:
                dat = json.load(fd)
            res = self.Dbgereum.verify_offline_data(dat)
            if res != 0:
                self.Dbgereum.data = dat
                messagebox.showinfo(title = "Done", message = "The data has successfully loaded")
            else:
                messagebox.showwarning(title = "Error", message = "Json invalid")
        except:
            nothing = 0

    def onOverAsRaw(self, root):
        try:
            dat = json.load(simpledialog.askstring("Txn data", "Input txn data:", parent = root))
            res = self.Dbgereum.verify_offline_data(dat)
            if res != 0:
                self.Dbgereum.data = dat
                messagebox.showinfo(title = "Done", message = "The data has successfully loaded")
            else:
                messagebox.showwarning(title = "Error", message = "Json invalid")
        except:
            nothing = 0

    def onWebImport(self, root):
        try:
            txn = simpledialog.askstring("Txn hash", "Input txn hash:", parent = root)
            dat = self.Dbgereum.parse_online_data(txn)
            if dat != "0":
                self.Dbgereum.data = dat
                messagebox.showerror(title = "Done", message = "The data has successfully loaded")
            else:
                messagebox.showwarning(title = "Error", message = "Hash invalid or connectivity issue")
        except:
            nothing = 0

    def onOpcodes(self, dis_text):
        cursor = dis_text.index(INSERT)
        if self.Dbgereum.opcodes == 0:
            self.Dbgereum.opcodes = 1
        else:
            self.Dbgereum.opcodes = 0
        self.disassemble(dis_text)
        dis_text.focus_set()
        dis_text.mark_set("insert", cursor)
        dis_text.yview(self.Dbgereum.line - 10)            

    def getOffset(self, text = None):
        cursor = text.index(INSERT)
        cur = cursor[:cursor.find(".")]
        line = text.get(cur + ".0", str(int(cur) + 1) + ".0")[6:]
        return line[:line.find(" ")]

    def find(self, entry = None, dis_text = None, stack_text = None, memory_text = None, storage_text = None):
        windows = [dis_text, stack_text, memory_text, storage_text]
        txt = ["Disasm", "Stack", "Memory", "Storage"]
        self.disassemble(dis_text)
        self.printStack(stack_text)
        self.printMemory(memory_text)
        self.printStorage(storage_text)
        for i in range(0, 4):
            ent = entry[i].get()
            if ent != "":
                
                k = "1.0"
                value = ent
                found = 0
                while(True):
                    try:
                        k = windows[i].search(value, k, nocase = 1, stopindex = END)
                    except:
                        windows[i].focus_set()
                        windows[i].mark_set("insert", k)
                        break
                    if not k:
                        if found == 0:
                            messagebox.showwarning(title = "Error", message = "Not Found in " + txt[i])
                        break
                    found = 1
                    ind = int(k[k.find(".") + 1:])
                    windows[i].tag_add('found', k, k[:k.find(".")] + "." + str(len(value) + ind))
                    windows[i].tag_config('found', foreground = 'magenta')
                    k = k[:k.find(".")] + "." + str(len(value) + ind)
                    #windows[i].focus_set()
                    #windows[i].mark_set("insert", k)
                    #windows[i].yview(int(k[:k.find(".")]) - 10)

    def keyProcessingFind(self, event, entry = None, dis_text = None, stack_text = None, memory_text = None, storage_text = None):
        if (event.keysym == 'Return'):
            self.find(entry, dis_text, stack_text, memory_text, storage_text)
            return "break"

    def findListener(self, dis_text, stack_text, memory_text, storage_text):
        sb = Tk()
        sb.title("Find")

        ent = [None] * 4
        lbl = [None] * 4
        txt = ["Disasm", "Stack", "Memory", "Storage"]

        sb.columnconfigure(0, pad = 3)
        sb.columnconfigure(1, pad = 3)
        sb.configure(background = "black")

        for i in range(0, 4):
            ent[i] = Entry(sb, width = 64, highlightthickness = 1, background = "black", foreground = "white", highlightcolor = "red", highlightbackground = "gray", insertbackground = "white")
            ent[i].configure(font = platform_font[platform])
            lbl[i] = Label(sb, bg = "black", fg = "white", text = txt[i])
            sb.rowconfigure(i, pad = 3)
            lbl[i].grid(row = i, column = 0)
            ent[i].grid(row = i, column = 1, stick = W + E)
        
        btn1 = Button(sb, text = "Find", activeforeground = "magenta", highlightbackground = "black", command = lambda: self.find(ent, dis_text, stack_text, memory_text, storage_text))
        btn1.grid(row = 4, column = 1, sticky = W + E)
        sb.bind("<Key>", lambda e: self.keyProcessingFind(e, ent, dis_text, stack_text, memory_text, storage_text))

        sb.mainloop()

    def keyProcessingMain(self, event, dis_text, stack_text, memory_text, storage_text):
        if (event.keysym == 'F8'):
            self.Step(dis_text, stack_text, memory_text, storage_text)
            return "break"

        elif (event.keysym == 'F9'):
            self.Run(dis_text, stack_text, memory_text, storage_text)
            return "break"

        else:
            return "break"

    def keyProcessingStorage(self, event, root, dis_text, stack_text, memory_text, storage_text):
        if (event.state == 4 and event.keysym == 'c'):
            return

        elif (event.state == 8 and event.keysym == 'c'):
            return

        elif (event.state == 4 and event.keysym == 'a'):
            storage_text.tag_add(SEL, "1.0", END)
            return "break"

        elif (event.state == 8 and event.keysym == 'a'):
            return

        elif (event.state == 4 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return

        elif (event.state == 8 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return
        
        elif (event.keysym == 'Up'):
            return

        elif (event.keysym == 'Down'):
            return

        elif (event.keysym == 'Right'):
            return
        
        elif (event.keysym == 'Left'):
            return

        elif (event.keysym == 'F4'): # update storage
            cursor = storage_text.index(INSERT)
            ind = int(cursor[:cursor.find(".")]) - 1
            txt = storage_text.get(str(ind + 1) + ".7", str(ind + 1) + ".72")
            try:
                value = simpledialog.askstring("Edit Storage", "Edit storage value:", initialvalue = hex(int(txt, 16))[2:], parent = root)[:64]
            except:
                value = txt
            try:
                int(value, 16) # check for non hex input
            except:
                storage_text.focus_set()
                storage_text.mark_set("insert", cursor)
                return "break"
            old = self.Dbgereum.storage[ind // 2]
            if ind % 2 == 0:
                self.Dbgereum.storage[ind // 2] = value + ":" + old[old.find(":") + 1:]
            else:
                self.Dbgereum.storage[ind // 2] = old[:old.find(":")] + ":" + value
            self.printStorage(storage_text)
            storage_text.focus_set()
            storage_text.mark_set("insert", cursor)
            return "break"

        elif (event.keysym == 'F8'):
            self.Step(dis_text, stack_text, memory_text, storage_text)
            return "break"

        elif (event.keysym == 'F9'):
            self.Run(dis_text, stack_text, memory_text, storage_text)
            return "break"

        else:
            return "break"

    def keyProcessingMemory(self, event, root, dis_text, stack_text, memory_text, storage_text):
        if (event.state == 4 and event.keysym == 'c'):
            return

        elif (event.state == 8 and event.keysym == 'c'):
            return

        elif (event.state == 4 and event.keysym == 'a'):
            memory_text.tag_add(SEL, "1.0", END)
            return "break"

        elif (event.state == 8 and event.keysym == 'a'):
            return

        elif (event.state == 4 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return

        elif (event.state == 8 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return
        
        elif (event.keysym == 'Up'):
            return

        elif (event.keysym == 'Down'):
            return

        elif (event.keysym == 'Right'):
            return
        
        elif (event.keysym == 'Left'):
            return

        # when we update memory, then memory_size EVM variable NOT CHANGES!!!
        elif (event.keysym == 'F4'): # update memory
            cursor = memory_text.index(INSERT)
            ind = (int(cursor[:cursor.find(".")]) - 1) * 32
            txt = memory_text.get(str(ind + 1) + ".7", str(ind + 1) + ".72")
            try:
                value = simpledialog.askstring("Edit Memory", "Edit memory value:", initialvalue = hex(int(txt, 16))[2:], parent = root)[:64]
            except:
                value = txt
            try:
                int(value, 16) # check for non hex input
            except:
                memory_text.focus_set()
                memory_text.mark_set("insert", cursor)
                return "break"
            length = 64 - len(value)
            for k in range(0, length):
                value = "0" + value
            i = 0
            k = 0
            while k != 64:
                self.Dbgereum.memory[ind + i] = value[k:k + 2]
                i += 1
                k += 2
            self.printMemory(memory_text)
            memory_text.focus_set()
            memory_text.mark_set("insert", cursor)
            return "break"

        elif (event.keysym == 'F8'):
            self.Step(dis_text, stack_text, memory_text, storage_text)
            return "break"

        elif (event.keysym == 'F9'):
            self.Run(dis_text, stack_text, memory_text, storage_text)
            return "break"

        else:
            return "break"

    def keyProcessingStack(self, event, root, dis_text, stack_text, memory_text, storage_text):
        if (event.state == 4 and event.keysym == 'c'):
            return

        elif (event.state == 8 and event.keysym == 'c'):
            return

        elif (event.state == 4 and event.keysym == 'a'):
            stack_text.tag_add(SEL, "1.0", END)
            return "break"

        elif (event.state == 8 and event.keysym == 'a'):
            return

        elif (event.state == 4 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return

        elif (event.state == 8 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return
        
        elif (event.keysym == 'Up'):
            return

        elif (event.keysym == 'Down'):
            return

        elif (event.keysym == 'Right'):
            return
        
        elif (event.keysym == 'Left'):
            return

        elif (event.keysym == 'F4'): # update stack
            cursor = stack_text.index(INSERT)
            ind = int(cursor[:cursor.find(".")]) - 1
            txt = stack_text.get(str(ind + 1) + ".7", str(ind + 1) + ".72")
            try: 
                value = simpledialog.askstring("Edit Stack", "Edit stack value:", initialvalue = hex(int(txt, 16))[2:], parent = root)[:64]
            except:
                value = txt
            try:
                int(value, 16) # check for non hex input
            except:
                stack_text.focus_set()
                stack_text.mark_set("insert", cursor)
                return "break"
            self.Dbgereum.stack[ind] = value
            self.printStack(stack_text)
            stack_text.focus_set()
            stack_text.mark_set("insert", cursor)
            return "break"

        elif (event.keysym == 'F8'):
            self.Step(dis_text, stack_text, memory_text, storage_text)
            return "break"

        elif (event.keysym == 'F9'):
            self.Run(dis_text, stack_text, memory_text, storage_text)
            return "break"

        else:
            return "break"

    def keyProcessing(self, event, root, dis_text, stack_text, memory_text, storage_text):
        if (event.state == 4 and event.keysym == 'c'):
            return

        elif (event.state == 8 and event.keysym == 'c'):
            return

        elif (event.state == 4 and event.keysym == 'a'):
            dis_text.tag_add(SEL, "1.0", END)
            return "break"

        elif (event.state == 8 and event.keysym == 'a'):
            return

        elif (event.state == 4 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return

        elif (event.state == 8 and event.keysym == 'f'):
            self.findListener(dis_text, stack_text, memory_text, storage_text)
            return
        
        elif (event.keysym == 'Up'):
            return

        elif (event.keysym == 'Down'):
            return
        
        elif (event.keysym == 'Right'):
            return
        
        elif (event.keysym == 'Left'):
            return

        elif (event.keysym == 'F4'): # change instruction pointer
            cursor = dis_text.index(INSERT)
            try: 
                value = simpledialog.askstring("Edit instruction pointer", "Edit offset(hex):", initialvalue = hex(self.Dbgereum.ip), parent = root)[:64]
            except:
                value = hex(self.Dbgereum.ip)
            try:
                int(value, 16)
            except:
                dis_text.focus_set()
                dis_text.mark_set("insert", cursor)
                return "break"
            ip, ln = self.Dbgereum.detectIP(int(value, 16))
            if ip != -1:
                self.redrawInstructionPointer(dis_text, ln)
                self.Dbgereum.ip = ip
                self.scrollToInstruction(dis_text, ln)
            else:
                messagebox.showwarning(title="Error", message="Invalid offset")
            dis_text.focus_set()
            dis_text.mark_set("insert", cursor)
            return "break"

        elif (event.keysym == 'F8'):
            self.Step(dis_text, stack_text, memory_text, storage_text)
            return "break"

        elif (event.keysym == 'F9'):
            self.Run(dis_text, stack_text, memory_text, storage_text)
            return "break"

        elif (event.keysym == 'F2'): # breakpoint
            cursor = dis_text.index(INSERT)
            offset = self.getOffset(dis_text)
            try:
                self.Dbgereum.breakpoints[offset]
                del self.Dbgereum.breakpoints[offset]
                # draw (delete breakpoint GUI)
                dis_text.delete(cursor[:cursor.find(".")] + ".0", cursor[:cursor.find(".")] + ".2")
                dis_text.insert(cursor[:cursor.find(".")] + ".0", "  ", "1")
            except:
                self.Dbgereum.breakpoints.update({offset:1})
                # draw (set breakpoint GUI)
                dis_text.delete(cursor[:cursor.find(".")] + ".0", cursor[:cursor.find(".")] + ".2")
                dis_text.insert(cursor[:cursor.find(".")] + ".0", ">>", "1")
            # I have used self.disassmble(dis_text) earlier.
            # In real huge smart contracts it's so many times needs to redraw disasm window
            # So I moved forward to implementation like here above.
            self.scrollToInstruction(dis_text, int(cursor[:cursor.find(".")]))
            dis_text.focus_set()
            dis_text.mark_set("insert", cursor)
            return "break"

        elif (event.keysym == 'F1'): # comment
            cursor = dis_text.index(INSERT)
            offset = self.getOffset(dis_text)
            try:
                try:
                    initial = self.Dbgereum.comments[int(offset, 16)]
                except:
                    initial = ""
                comment = simpledialog.askstring("Comment", "Input your comment(40 symbols per line):", initialvalue = initial, parent = root)[:40]
                self.Dbgereum.comment(int(offset, 16), comment)
            except:
                return "break"
            # draw (comment GUI)
            if self.Dbgereum.opcodes:
                dis_text.delete(cursor[:cursor.find(".")] + ".114", cursor[:cursor.find(".")] + ".154")
                dis_text.insert(cursor[:cursor.find(".")] + ".114", comment, "6")
            else:
                dis_text.delete(cursor[:cursor.find(".")] + ".108", cursor[:cursor.find(".")] + ".154")
                dis_text.insert(cursor[:cursor.find(".")] + ".108", comment, "5")
            # I have used self.disassmble(dis_text) earlier.
            # In real huge smart contracts it's so many times needs to redraw disasm window
            # So I moved forward to implementation like here above.
            self.scrollToInstruction(dis_text, int(cursor[:cursor.find(".")]))
            dis_text.focus_set()
            dis_text.mark_set("insert", cursor)
            return "break"

        else:
            return "break"

    # It helps to draw IP instead of redraw all disasm window in disassmble()
    def redrawInstructionPointer(self, text, line):
        br_start = text.tag_ranges("breakp")[0]
        br_stop = text.tag_ranges("breakp")[1]
        text.delete(br_start, br_stop)
        text.insert(br_start, "    ", "1")
        text.delete(str(line) + ".2", str(line) + ".6")
        text.insert(str(line) + ".2", "    ", "breakp")

    def scrollToInstruction(self, text, line):
        text.yview(line - 10) # DEBUG MAGENTA SCROLLING = MINUS 10

    def Step(self, dis_text, stack_text, memory_text, storage_text):
        ret = self.Dbgereum.exec(self.Dbgereum.ip)
        if ret == 0xfd:
            messagebox.showwarning(title = "REVERT", message = "Execution reverted")
        if ret == 0xff:
            messagebox.showwarning(title = "SELFDESTRUCT", message = "Smart contract selfdesctructed")
        if ret == 0x00:
            messagebox.showwarning(title = "STOP", message = "Execution stopped")
        if ret == 0xf3:
            messagebox.showwarning(title = "RETURN", message = "Execution stopped. Data returned.")
        if ret == 0x1000:
            messagebox.showwarning(title = "Issue", message = "Balance underflow")
        if ret == 0x1001:
            messagebox.showwarning(title = "Issue", message = "Balance overflow")

        ip, ln = self.Dbgereum.detectIP(self.Dbgereum.ip)
        # I have used self.disassmble(dis_text) earlier.
        # In real huge smart contracts it's so many times needs to redraw disasm window
        # So I moved forward to implementation like here below.
        self.redrawInstructionPointer(dis_text, ln)
        self.scrollToInstruction(dis_text, ln)
        self.printStack(stack_text)
        self.printMemory(memory_text)
        self.printStorage(storage_text)
    
    def Run(self, dis_text, stack_text, memory_text, storage_text):
        self.Step(dis_text, stack_text, memory_text, storage_text)
        res = None
        while res == None:
            try:
                self.Dbgereum.breakpoints[hex(self.Dbgereum.ip)] # if self.ip contains in breakpoints list then stop. else execute.
                break
            except:
                res = self.Dbgereum.exec(self.Dbgereum.ip)
        if res != None:
            self.Step(dis_text, stack_text, memory_text, storage_text)
        ip, ln = self.Dbgereum.detectIP(self.Dbgereum.ip)
        # I have used self.disassmble(dis_text) earlier.
        # In real huge smart contracts it's so many times needs to redraw disasm window
        # So I moved forward to implementation like here below.
        self.redrawInstructionPointer(dis_text, ln)
        self.scrollToInstruction(dis_text, ln)
        self.printStack(stack_text)
        self.printMemory(memory_text)
        self.printStorage(storage_text)
    
    def Restart(self, dis_text, stack_text, memory_text, storage_text):
        self.Dbgereum.flushObject()
        self.Dbgereum.getLastOffset()
        self.Dbgereum.init_memory()
        self.Dbgereum.init_storage()
        self.printStack(stack_text)
        self.printMemory(memory_text)
        self.printStorage(storage_text)
        self.disassemble(dis_text)
        return

    def disassemble(self, text = None):

        text.delete('1.0', END)
        end = len(self.Dbgereum.bytecode)
        i = 0
        current_line = 1
        while i != end:
            
            comment = ""
            try:
                comment = self.Dbgereum.comments[i]
            except:
                nothing = 0
            
            breakp = ""
            try:
                self.Dbgereum.breakpoints[hex(i)]
                breakp = ">>"
            except:
                nothing = 0

            _offset = i

            # print instructions
            try:
                byte = self.Dbgereum.bytecode[i]
                instruction = _table[byte][0]

                if instruction == "PUSH":
                    operand_size = _table[byte][1]
                    parameter = ""
                    check = 0

                    # It needs just for beautiful value representation O__o
                    for k in range(0, operand_size):
                        check += int(self.Dbgereum.bytecode[i + k + 1])
                        if check != 0 or operand_size == 1:
                            parameter += ''.join('{:02x}'.format(self.Dbgereum.bytecode[i + k + 1]))

                    if self.Dbgereum.opcodes:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{hex(self.Dbgereum.bytecode[i])[2:]:<6}" + f"{instruction + str(operand_size):<18}" + f"{'0x' + parameter:<72}" + comment + "\n")
                    else:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}"  + f"{instruction + str(operand_size):<18}" + f"{'0x' + parameter:<72}" + comment + "\n")
                    i += operand_size

                elif instruction == "DUP":
                    ins = _table[byte][2]
                    if self.Dbgereum.opcodes:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{hex(self.Dbgereum.bytecode[i])[2:]:<6}" + f"{instruction + str(ins):<90}" + comment + "\n")
                    else:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{instruction + str(ins):<90}" + comment + "\n")
                
                elif instruction == "SWAP":
                    ins = _table[byte][2] - 1
                    if self.Dbgereum.opcodes:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{hex(self.Dbgereum.bytecode[i])[2:]:<6}" + f"{instruction + str(ins):<90}" + comment + "\n")
                    else:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{instruction + str(ins):<90}" + comment + "\n")

                else:
                    if self.Dbgereum.opcodes:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{hex(self.Dbgereum.bytecode[i])[2:]:<6}" + f"{instruction:<90}" + comment + "\n")
                    else:
                        text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{instruction:<90}" + comment + "\n")
            except:
                if self.Dbgereum.opcodes:
                    text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{hex(self.Dbgereum.bytecode[i])[2:]:<6}" + f"{'WTF':<90}" + comment + "\n")
                else:
                    text.insert(INSERT, f"{breakp:<6}" + f"{hex(i):<12}" + f"{'WTF':<90}" + comment + "\n")
            if self.Dbgereum.opcodes:
                self.add_color(text, current_line, _offset, 1)
            else:
                self.add_color(text, current_line, _offset, 0)
            # check for jumps and exits
            current_line += 1
            if instruction == "JUMP" or instruction == "JUMPI" or instruction == "REVERT" or instruction == "STOP":
                if self.Dbgereum.opcodes:
                    text.insert(INSERT, f"{'':<6}" + "------------------------------------------------------------------------------------------------------" + "\n")
                    text.tag_add("1", str(current_line) + ".0", str(current_line) + ".6")
                    text.tag_add("2", str(current_line) + ".6", str(current_line) + ".108")
                    text.tag_config("1", foreground="red")
                    text.tag_config("2", foreground="gray")
                else:
                    text.insert(INSERT, f"{'':<6}" + "------------------------------------------------------------------------------------------------" + "\n")
                    text.tag_add("1", str(current_line) + ".0", str(current_line) + ".6")
                    text.tag_add("2", str(current_line) + ".6", str(current_line) + ".102")
                    text.tag_config("1", foreground="red")
                    text.tag_config("2", foreground="gray")
                current_line += 1
            i += 1

    def add_color(self, text = None, current_line = None, offset = None, opcodes_enabled = 0):
        if opcodes_enabled == 1:
            if self.Dbgereum.ip == offset:
                text.tag_add("break", str(current_line) + ".0", str(current_line) + ".2")
                text.tag_add("breakp", str(current_line) + ".2", str(current_line) + ".6")
                self.Dbgereum.line = current_line
            else:
                text.tag_add("1", str(current_line) + ".0", str(current_line) + ".6")
            text.tag_add("2", str(current_line) + ".6", str(current_line) + ".18")
            text.tag_add("3", str(current_line) + ".18", str(current_line) + ".24")
            text.tag_add("4", str(current_line) + ".24", str(current_line) + ".42")
            text.tag_add("5", str(current_line) + ".42", str(current_line) + ".114")
            text.tag_add("6", str(current_line) + ".114", str(current_line) + ".154")
            if self.Dbgereum.ip == offset:
                text.tag_config("break", background="black", foreground="red")
                text.tag_config("breakp", background="magenta", foreground="red")
            else:
                text.tag_config("1", foreground="red")
            text.tag_config("2", foreground="gray")
            text.tag_config("3", foreground="yellow")
            text.tag_config("4", foreground="white")
            text.tag_config("5", foreground="cyan")
            text.tag_config("6", foreground="gray")
        else:
            if self.Dbgereum.ip == offset:
                text.tag_add("break", str(current_line) + ".0", str(current_line) + ".2")
                text.tag_add("breakp", str(current_line) + ".2", str(current_line) + ".6")
                self.Dbgereum.line = current_line
            else:
                text.tag_add("1", str(current_line) + ".0", str(current_line) + ".6")
            text.tag_add("2", str(current_line) + ".6", str(current_line) + ".18")
            text.tag_add("3", str(current_line) + ".18", str(current_line) + ".36")
            text.tag_add("4", str(current_line) + ".36", str(current_line) + ".108")
            text.tag_add("5", str(current_line) + ".108", str(current_line) + ".154")
            if self.Dbgereum.ip == offset:
                text.tag_config("break", background="black", foreground="red")
                text.tag_config("breakp", background="magenta", foreground="red")
            else:
                text.tag_config("1", foreground="red")
            text.tag_config("2", foreground="gray")
            text.tag_config("3", foreground="white")
            text.tag_config("4", foreground="cyan")
            text.tag_config("5", foreground="gray")

    def printStack(self, text = None):
        text.delete('1.0', END)
        for i in range(0, len(self.Dbgereum.stack)):
            value = str(self.Dbgereum.stack[i])
            length = 64 - len(value)
            for k in range(0, length):
                value = "0" + value
            text.insert(INSERT, f"{i:>6}:" + value)
            if len(self.Dbgereum.stack) - i != 1:
                text.insert(INSERT, "\n")
        text.yview(END)

    def printMemory(self, text = None):
        text.delete('1.0', END)
        for i in range(0, 1024):
            value = ""
            for k in range(0, 32):
                value += self.Dbgereum.memory[i * 32 + k] # memory stores hex values
            text.insert(INSERT, f"{hex(i * 2)[2:]:>5}0:" + value)
            if 1024 - i != 1:
                text.insert(INSERT, "\n")

    def printStorage(self, text = None):
        text.delete('1.0', END)
        try:
            i = 0
            line = self.Dbgereum.storage[i]
            while(1):
                key = line[:line.find(":")][:64]
                value = line[line.find(":") + 1:][:64]
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
                length = 64 - len(key)
                for k in range(0, length):
                    key = "0" + key
                text.insert(INSERT, f"{'':>7}" + key)
                text.insert(INSERT, "\n" + f"{'':>6}:" + value)
                i += 1
                line = self.Dbgereum.storage[i]
                text.insert(INSERT, "\n")
        except:
            nothing = 0


#######################################################
#          Main dbg object and logic with it          #
#######################################################


class Dbgereum:

    def __init__(self):
        self.bytecode = b''          # smart contract bytecode
        self.comments = {}           # list of comments
        self.ip = 0                  # instruction pointer offset
        self.line = 0                # instruction pointer line
        self.last_instruction = 0    # offset for the last opcode
        self.breakpoints = {}        # list of breakpints
        self.stack = []              # stores strings(hex values)!
        self.memory = []             # memory index:value
        self.memory_size = 0         # sizeof(memory)
        self.storage = []            # storage key:value
        self.gas_remaining = 0       # available gas from current instruction
        self.opcodes = 0             # view mode for opcodes [on/off]
        self.data = ""               # environment variables (json data)
    
    def flushObject(self):
        self.comments = {}
        self.ip = 0
        self.line = 0
        self.last_instruction = 0
        self.stack = []
        self.memory = []
        self.memory_size = 0
        self.storage = []
        self.gas_remaining = 0

    # check work for various smart contracts(opcodes)
    def calculateGas(self, gas):
        self.gas_remaining += gas

    def detectIP(self, ip = None):
        end = len(self.bytecode)
        i = 0
        previous = 0
        line = 1
        while i <= end:
            if ip == i:
                return ip, line
            elif ip < i:
                return previous, line
            previous = i
            try:
                byte = self.bytecode[i]
                instruction = _table[byte][0]

                if instruction == "PUSH":
                    operand_size = _table[byte][1]
                    i += operand_size
                if instruction == "JUMP" or instruction == "JUMPI" or instruction == "REVERT" or instruction == "STOP":
                    line += 1
            except:
                nothing = 0
            i += 1
            line += 1
        return -1, 1

    def getLastOffset(self):
        end = len(self.bytecode)
        while self.last_instruction <= end:
            try:
                byte = self.bytecode[self.last_instruction]
                instruction = _table[byte][0]
                self.calculateGas(_table[byte][4])

                if instruction == "PUSH":
                    operand_size = _table[byte][1]
                    self.last_instruction += operand_size
            except:
                nothing = 0
            self.last_instruction += 1
    
    def init_memory(self):
        for i in range(0, 1024):
            for k in range(0, 32):
                self.memory.append("00")

    def init_storage(self):
        try:
            fname = location + "STORAGE.dat"
            with open(fname, 'r') as fd:
                for line in fd:
                    line = line.rstrip()
                    self.storage.append(line)
        except:
            nothing = 0

    def parse_online_data(self, txn, isBytecodeParse = 0):
        try:
            if txn[0:2] != "0x":
                txn = "0x" + txn
            print("Please wait for web request processing...")
            r = requests.get('https://etherscan.io/tx/' + txn, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})
        
            i = r.text.find('contractCopy') + 29
            this_address = "000000000000000000000000" + r.text[i + 2:i + 42]

            addr = r.text[i:i + 42]
            r3 = requests.get('https://etherscan.io/address/' + addr, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})

            if isBytecodeParse != 0:
                i = r3.text.find('verifiedbytecode2') + 19
                k = r3.text[i:].find('<')
                self.bytecode = bytes.fromhex(r3.text[i:i + k])

            i = r3.text.find('Balance:') + 37
            k = r3.text[i:i + 100].find(' Ether')
            eth = r3.text[i:i + k]
            if "." in eth:
                i = eth.find(".") + 1
                value = (eth[i:] + "000000000000000000").replace("</b>", "")[:18]
                integer = eth[:i - 1].replace(",","").replace("<b>", "")
                value = integer + value
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            else:
                value = str(int(eth) * 1000000000000000000)
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            this_balance = value

            i = r.text.find('addressCopy') + 43
            tx_origin =  "000000000000000000000000" + r.text[i:i + 40] # implement correct tx.origin detect 'is FROM contract?'

            i = r.text.find('per GAS') + 32
            k = r.text[i:i + 100].find(' Ether')
            eth = r.text[i:i + 1] + "." + r.text[i + 9: i + k]
            if "." in eth:
                i = eth.find(".") + 1
                value = (eth[i:] + "000000000000000000")[:18]
                integer = eth[:i - 1]
                value = integer + value
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            else:
                value = str(int(eth) * 1000000000000000000)
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            tx_gasprice = value

            i = r.text.find('/block/') + 7
            k = r.text.find("'", i)
            value_dec = int(r.text[i:k])
            value = hex(value_dec)[2:]
            length = 64 - len(value)
            for k in range(0, length):
                value = "0" + value
            block_number = value
            
            r2 = requests.get('https://etherscan.io/block/' + str(value_dec), headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})
            
            i = r2.text.find('Hash:') + 37
            blockhash = r2.text[i:i + 64]

            i = r2.text.find('Mined by:') + 59
            block_coinbase = "000000000000000000000000" + r2.text[i:i + 40]
            
            import datetime
            i = r2.text.find('Timestamp:') + 57
            k1 = r2.text[i:i + 100].find("(") + 1
            k2 = r2.text[i:i + 100].find(")")
            date_str = r2.text[i + k1:i + k2]
            date = datetime.datetime.strptime(date_str, "%b-%d-%Y %I:%M:%S %p +UTC")
            block_timestamp = "00000000000000000000000000000000000000000000000000000000" + hex(int(datetime.datetime.timestamp(date)))[2:] # may be incorrect

            i = r2.text.find('Difficulty:') + 41
            k = r2.text[i:i + 100].find("<") - 1
            value = hex(int(r2.text[i:i + k].replace(",", "")))[2:]
            length = 64 - len(value)
            for k in range(0, length):
                value = "0" + value
            block_difficulty = value
            
            i = r2.text.find('Gas Limit:') + 40
            k = r2.text[i:i + 100].find("<") - 1
            value = hex(int(r2.text[i:i + k].replace(",", "")))[2:]
            length = 64 - len(value)
            for k in range(0, length):
                value = "0" + value
            block_gaslimit = value

            chain_id = "0000000000000000000000000000000000000000000000000000000000000001"

            i = r2.text.find('Base Fee Per Gas:') + 45
            k = r2.text[i:i + 100].find(" Ether")
            eth = r2.text[i:i + 1] + "." + r2.text[i + 9: i + k]
            if "." in eth:
                i = eth.find(".") + 1
                value = (eth[i:] + "000000000000000000").replace("</b>", "")[:18]
                integer = eth[:i - 1].replace(",","").replace("<b>", "")
                value = integer + value
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            else:
                value = str(int(eth) * 1000000000000000000)
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            base_fee = value

            i = r.text.find('addressCopy') + 43
            msg_caller = "000000000000000000000000" + r.text[i:i + 40]
            
            i = r.text.find(' Ether<')
            k = r.text[i - 40:i].find('>') # if constant will change then change constant below
            eth = r.text[i - 40 + k + 1:i] # here
            if "." in eth:
                i = eth.find(".") + 1
                value = (eth[i:] + "000000000000000000").replace("</b>", "")[:18]
                integer = eth[:i - 1]
                value = integer + value
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            else:
                value = str(int(eth) * 1000000000000000000)
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
            msg_value = value

            i = r.text.find('rawinput') + 33
            call_method = r.text[i:i + 10]
            k = r.text[i:].find("<")
            msg_data = r.text[i + 10:i + k]
            
            data = "{\"this_address\":\"" + this_address + "\",\"this_balance\":\"" + this_balance + "\",\"tx_origin\":\"" + tx_origin + "\",\"tx_gasprice\":\"" + tx_gasprice + "\",\"blockhash\":\"" + blockhash + "\",\"block_coinbase\":\"" + block_coinbase + "\",\"block_timestamp\":\"" + block_timestamp + "\",\"block_number\":\"" + block_number + "\",\"block_difficulty\":\"" + block_difficulty + "\",\"block_gaslimit\":\"" + block_gaslimit + "\",\"chain_id\":\"" + chain_id + "\",\"base_fee\":\"" + base_fee + "\",\"msg_caller\":\"" + msg_caller + "\",\"msg_value\":\"" + msg_value + "\",\"msg_data\":\"" + msg_data + "\"}"
            return json.loads(data)
        except:
            #Can't parse data from web!
            return "0"

    def verify_offline_data(self, dat):
        if len(dat) != 15:
            return 0
        if len(dat['this_address']) % 64 != 0:
            return 0
        if len(dat['this_balance']) % 64 != 0:
            return 0
        if len(dat['tx_origin']) % 64 != 0:
            return 0
        if len(dat['tx_gasprice']) % 64 != 0:
            return 0
        if len(dat['blockhash']) % 64 != 0:
            return 0
        if len(dat['block_coinbase']) % 64 != 0:
            return 0
        if len(dat['block_timestamp']) % 64 != 0:
            return 0
        if len(dat['block_number']) % 64 != 0:
            return 0
        if len(dat['block_difficulty']) % 64 != 0:
            return 0
        if len(dat['block_gaslimit']) % 64 != 0:
            return 0
        if len(dat['chain_id']) % 64 != 0:
            return 0
        if len(dat['base_fee']) % 64 != 0:
            return 0
        if len(dat['msg_caller']) % 64 != 0:
            return 0
        if len(dat['msg_value']) % 64 != 0:
            return 0
        if len(dat['msg_data']) % 64 != 0:
            return 0
        try:
            int(dat['this_address'], 16)
            int(dat['this_balance'], 16)
            int(dat['tx_origin'], 16)
            int(dat['tx_gasprice'], 16)
            int(dat['blockhash'], 16)
            int(dat['block_coinbase'], 16)
            int(dat['block_timestamp'], 16)
            int(dat['block_number'], 16)
            int(dat['block_difficulty'], 16)
            int(dat['block_gaslimit'], 16)
            int(dat['chain_id'], 16)
            int(dat['base_fee'], 16)
            int(dat['msg_caller'], 16)
            int(dat['msg_value'], 16)
            int(dat['msg_data'], 16)
        except:
            return 0
        return 1

    def comment(self, offset, comment):
        self.comments.update({offset:comment})

    def exec(self, index):
        command = self.bytecode[index]
        self.gas_remaining -= _table[command][4]

        #STOP
        if command == 0x00:
            return 0

        #JUMP
        elif command == 0x56:
            location = 0
            try:
                location = int(self.stack.pop(), 16)
                self.ip = location
            except:
                print("[JUMP] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #JUMPI
        elif command == 0x57:
            location = 0
            condition = 0
            try:
                location = int(self.stack.pop(), 16)
                condition = int(self.stack.pop())
                if condition:
                    self.ip = location
                else:
                    self.ip += 1
            except:
                print("[JUMPI] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #PUSH
        elif _table[command][0] == "PUSH":
            size = _table[command][1]
            parameter = ""
            for i in range(0, size):
                parameter += '{:02x}'.format(self.bytecode[index + i + 1])
            self.stack.append(parameter)
            self.ip += size + 1

        #POP
        elif command == 0x50:
            try:
                self.stack.pop()
                self.ip += 1
            except:
                print("[POP] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #DUP
        elif _table[command][0] == "DUP":
            size = _table[command][2]
            if size <= len(self.stack):
                duplicate = self.stack[len(self.stack) - size]
                self.stack.append(duplicate)
                self.ip += 1
            else:
                print("[DUP] Smth went wrong :( - Trying to access incorrect index on the stack")
                exit()
        
        #SWAP
        elif _table[command][0] == "SWAP":
            size = _table[command][2] - 1
            if size < len(self.stack):
                duplicate = self.stack[len(self.stack) - 1 - size]
                self.stack[len(self.stack) - size] = self.stack.pop()
                self.stack.append(duplicate)
                self.ip += 1
            else:
                print("[SWAP] Smth went wrong :( - Trying to access incorrect index on the stack")
                exit()
        
        #JUMPDEST
        elif command == 0x5b:
            self.ip += 1

        #ADD
        elif command == 0x01:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                self.stack.append(hex((op1 + op2) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)[2:])
                self.ip += 1
            except:
                print("[ADD] Smth went wrong :( - Popped value from empty stack...")
                exit()
        
        #MUL
        elif command == 0x02:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                self.stack.append(hex((op1 * op2) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)[2:])
                self.ip += 1
            except:
                print("[MUL] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SUB
        elif command == 0x03:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op1 < op2:
                    self.stack.append(hex((op1 - op2) + 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)[2:]) # CORRECT?
                else:
                    self.stack.append(hex(op1 - op2)[2:])
                self.ip += 1
            except:
                print("[SUB] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #DIV
        elif command == 0x04:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op2 == 0:
                    print("[DIV] Error. Division by zero")
                    exit()
                self.stack.append(hex(op1 // op2)[2:]) # CORRECT?
                self.ip += 1
            except:
                print("[DIV] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SDIV
        elif command == 0x05:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op2 == 0:
                    print("[SDIV] Error. Division by zero")
                    exit()
                sign = 0
                if op1 > 0x8000000000000000000000000000000000000000000000000000000000000000:
                    op1 = 0x10000000000000000000000000000000000000000000000000000000000000000 - op1
                    sign ^= 1
                if op2 > 0x8000000000000000000000000000000000000000000000000000000000000000:
                    op2 = 0x10000000000000000000000000000000000000000000000000000000000000000 - op2
                    sign ^= 1
                res = op1 // op2
                if sign == 1:
                    res = 0x10000000000000000000000000000000000000000000000000000000000000000 - res
                self.stack.append(hex(res)[2:]) # CORRECT?
                self.ip += 1
            except:
                print("[SDIV] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #MOD
        elif command == 0x06:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op2 == 0:
                    print("[MOD] Error. Division by zero")
                    exit()
                self.stack.append(hex(op1 % op2)[2:])
                self.ip += 1
            except:
                print("[MOD] Smth went wrong :( - Popped value from empty stack...")
                exit()
        
        #SMOD
        elif command == 0x07:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op2 == 0:
                    print("[SMOD] Error. Division by zero")
                    exit()
                res = op1 % op2
                if op1 < 0:
                    res -= op2 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                self.stack.append(hex(res)[2:]) # CORRECT?
                self.ip += 1
            except:
                print("[SMOD] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #ADDMOD
        elif command == 0x08:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                op3 = int(self.stack.pop(), 16)
                if op3 == 0:
                    print("[ADDMOD] Error. Division by zero")
                    exit()
                self.stack.append(hex(((op1 + op2) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) % op3)[2:])
                self.ip += 1
            except:
                print("[ADDMOD] Smth went wrong :( - Popped value from empty stack...")
                exit()
        
        #MULMOD
        elif command == 0x09:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                op3 = int(self.stack.pop(), 16)
                if op3 == 0:
                    print("[MULMOD] Error. Division by zero")
                    exit()
                self.stack.append(hex(((op1 * op2) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) % op3)[2:])
                self.ip += 1
            except:
                print("[MULMOD] Smth went wrong :( - Popped value from empty stack...")
                exit()
        #EXP
        elif command == 0x0a:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                self.stack.append(hex(op1 ** op2)[2:])
                self.ip += 1
            except:
                print("[EXP] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SIGNEXTEND
        # represent values 
        elif command == 0x0b:
            try:
                b = int(self.stack.pop(), 16)
                x = int(self.stack.pop(), 16)
                msb = x >> ((b + 1) * 8 - 1)
                if msb == 1:
                    x &= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                self.stack.append(hex(x)[2:])
                self.ip += 1
            except:
                print("[SIGNEXTEND] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #LT
        elif command == 0x10:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op1 < op2:
                    self.stack.append(hex(1)[2:])
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[LT] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #GT
        elif command == 0x11:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op1 > op2:
                    self.stack.append(hex(1)[2:])
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[GT] Smth went wrong :( - Popped value from empty stack...")
                exit()
        
        #SLT
        elif command == 0x12:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op1 > 0x8000000000000000000000000000000000000000000000000000000000000000:
                    op1 -= 0x10000000000000000000000000000000000000000000000000000000000000000
                if op2 > 0x8000000000000000000000000000000000000000000000000000000000000000:
                    op2 -= 0x10000000000000000000000000000000000000000000000000000000000000000
                if op1 < op2:
                    self.stack.append(hex(1)[2:])
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[SLT] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SGT
        elif command == 0x13:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op1 > 0x8000000000000000000000000000000000000000000000000000000000000000:
                    op1 -= 0x10000000000000000000000000000000000000000000000000000000000000000
                if op2 > 0x8000000000000000000000000000000000000000000000000000000000000000:
                    op2 -= 0x10000000000000000000000000000000000000000000000000000000000000000
                if op1 > op2:
                    self.stack.append(hex(1)[2:])
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[SGT] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #EQ
        elif command == 0x14:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                if op1 == op2:
                    self.stack.append(hex(1)[2:])
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[EQ] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #ISZERO
        elif command == 0x15:
            try:
                op1 = int(self.stack.pop(), 16)
                if op1 == 0:
                    self.stack.append(hex(1)[2:])
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[ISZERO] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #AND
        elif command == 0x16:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                self.stack.append(hex(op1 & op2)[2:])
                self.ip += 1
            except:
                print("[AND] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #OR
        elif command == 0x17:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                self.stack.append(hex(op1 | op2)[2:])
                self.ip += 1
            except:
                print("[OR] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #XOR
        elif command == 0x18:
            try:
                op1 = int(self.stack.pop(), 16)
                op2 = int(self.stack.pop(), 16)
                self.stack.append(hex(op1 ^ op2)[2:])
                self.ip += 1
            except:
                print("[XOR] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #NOT
        elif command == 0x19:
            try:
                op1 = int(self.stack.pop(), 16)
                op1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF - op1
                self.stack.append(hex(op1)[2:])
                self.ip += 1
            except:
                print("[NOT] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #BYTE
        elif command == 0x1a:
            try:
                i = int(self.stack.pop(), 16)
                x = int(self.stack.pop(), 16)
                res = (x >> (248 - i * 8)) & 0xFF
                self.stack.append(hex(res)[2:])
                self.ip += 1
            except:
                print("[BYTE] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SHL
        elif command == 0x1b:
            try:
                shift = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                result = value << shift
                # Make sure we are still in 32 byte range
                result &= 2**256 - 1 # 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                self.stack.append(hex(result)[2:])
                self.ip += 1
            except:
                print("[SHL] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SHR
        elif command == 0x1c:
            try:
                shift = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                self.stack.append(hex(value >> shift)[2:])
                self.ip += 1
            except:
                print("[SHR] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SAR
        elif command == 0x1d:
            try:
                shift = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                msb = value & 0x8000000000000000000000000000000000000000000000000000000000000000
                if msb != 0:
                    for i in range (0, shift):
                        value >>= 1
                        value |= 0x8000000000000000000000000000000000000000000000000000000000000000
                else:
                    value >>= shift
                self.stack.append(hex(value)[2:])
                self.ip += 1
            except:
                print("[SAR] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SHA3
        elif command == 0x20:
            try:
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)
                res = bytes(int(byte, 16) for byte in self.memory[offset:offset + length])
                k = keccak.new(digest_bits=256)
                k.update(res)
                res = k.hexdigest()
                self.stack.append(res)
                self.ip += 1
            except:
                print("[SHA3] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #MLOAD
        elif command == 0x51:
            try:
                index = int(self.stack.pop(), 16)
                self.stack.append(self.memory[index])
                self.memory_size -= 32
                self.ip += 1
            except:
                print("[MLOAD] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #MSTORE
        elif command == 0x52:
            try:
                index = int(self.stack.pop(), 16)
                value = hex(int(self.stack.pop(), 16))[2:]
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
                k = 0
                i = 0
                while k != 64:
                    self.memory[index + i] = value[k:k + 2]
                    k += 2
                    i += 1
                self.memory_size += 32
                self.ip += 1
            except:
                print("[MSTORE] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #MSTORE8
        elif command == 0x53:
            try:
                index = int(self.stack.pop(), 16)
                value = hex(int(self.stack.pop(), 16) & 0xFF)[2:]
                self.memory[index] = value
                self.memory_size += 1
                self.ip += 1
            except:
                print("[MSTORE8] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SLOAD
        elif command == 0x54:
            try:
                key = int(self.stack.pop(), 16)
                for i in range(len(self.storage) - 1, 0, -1):
                    if int(self.storage[i].split(":")[0], 16) == key:
                        self.stack.append(self.storage[i].split(":")[1])
                        break
                else:
                    self.stack.append(hex(0)[2:])
                self.ip += 1
            except:
                print("[SLOAD] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #SSTORE
        elif command == 0x55:
            try:
                key = self.stack.pop()
                value = hex(int(self.stack.pop(), 16))[2:]
                self.storage.append(key + ":" + value)
                self.ip += 1
            except:
                print("[SSTORE] Smth went wrong :( - Popped value from empty stack...")
                exit()

        #GETPC
        elif command == 0x58:
            try:
                self.stack.append(self.ip)
                self.ip += 1
            except:
                print("[GETPC] Smth went wrong :( - Popped value from empty stack...")
                exit()
        
        #MSIZE
        elif command == 0x59:
            try:
                self.stack.append(self.memory_size)
                self.ip += 1
            except:
                print("[MSIZE] Smth went wrong :(")
                exit()

        #GAS
        elif command == 0x5a:
            try:
                self.stack.append(self.gas_remaining)
                self.ip += 1
            except:
                print("[GAS] Smth went wrong :(")
                exit()

        #LOG0
        elif command == 0xa0:
            try:
                offset = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                #FIRE AN EVENT. NEED TO IMPLEMENT??? NOT SURE
                self.ip += 1
            except:
                print("[LOG0] Smth went wrong :(")
                exit()
        
        #LOG1
        elif command == 0xa1:
            try:
                offset = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                topic0 = int(self.stack.pop(), 16)
                #FIRE AN EVENT. NEED TO IMPLEMENT??? NOT SURE
                self.ip += 1
            except:
                print("[LOG1] Smth went wrong :(")
                exit()

        #LOG2
        elif command == 0xa2:
            try:
                offset = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                topic0 = int(self.stack.pop(), 16)
                topic1 = int(self.stack.pop(), 16)
                #FIRE AN EVENT. NEED TO IMPLEMENT??? NOT SURE
                self.ip += 1
            except:
                print("[LOG2] Smth went wrong :(")
                exit()

        #LOG3
        elif command == 0xa3:
            try:
                offset = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                topic0 = int(self.stack.pop(), 16)
                topic1 = int(self.stack.pop(), 16)
                topic2 = int(self.stack.pop(), 16)
                #FIRE AN EVENT. NEED TO IMPLEMENT??? NOT SURE
                self.ip += 1
            except:
                print("[LOG3] Smth went wrong :(")
                exit()

        #LOG4
        elif command == 0xa4:
            try:
                offset = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                topic0 = int(self.stack.pop(), 16)
                topic1 = int(self.stack.pop(), 16)
                topic2 = int(self.stack.pop(), 16)
                topic3 = int(self.stack.pop(), 16)
                #FIRE AN EVENT. NEED TO IMPLEMENT??? NOT SURE
                self.ip += 1
            except:
                print("[LOG4] Smth went wrong :(")
                exit()
        
        #ADDRESS
        elif command == 0x30:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                self.stack.append(self.data['this_address'])
                self.ip += 1
            except:
                print("[ADDRESS] Smth went wrong with input :(")
                exit()

        #BALANCE
        elif command == 0x31:
            try:
                # Instruction where we can use our fuzzer!
                address = self.stack.pop()[24:64]
                r3 = requests.get('https://etherscan.io/address/0x' + address, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})

                i = r3.text.find('Balance:') + 37
                k = r3.text[i:i + 100].find(' Ether')
                eth = r3.text[i:i + k]
                if "." in eth:
                    i = eth.find(".") + 1
                    value = (eth[i:] + "000000000000000000")[:18]
                    integer = eth[:i - 1]
                    value = integer + value
                    length = 64 - len(value)
                    for k in range(0, length):
                        value = "0" + value
                else:
                    value = str(int(eth) * 1000000000000000000)
                    length = 64 - len(value)
                    for k in range(0, length):
                        value = "0" + value

                self.stack.append(value)
                self.ip += 1
            except:
                print("[BALANCE] Smth went wrong :( - Popped value from empty stack or API request not working.")
                exit()
        
        #ORIGIN
        elif command == 0x32:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                self.stack.append(self.data['tx_origin'])
                self.ip += 1
            except:
                print("[ORIGIN] Smth went wrong with input :(")
                exit()

        #CALLER
        elif command == 0x33:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                self.stack.append(self.data['msg_caller'])
                self.ip += 1
            except:
                print("[CALLER] Smth went wrong with input :(")
                exit()

        #CALLVALUE
        elif command == 0x34:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                self.stack.append(self.data['msg_value'])
                self.ip += 1
            except:
                print("[CALLVALUE] Smth went wrong with input :(")
                exit()

        #CALLDATALOAD
        elif command == 0x35:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                i = int(self.stack.pop(), 16)
                msg_data = ""
                for k in range(0, 64):
                    msg_data += self.data['msg_data'][i * 64 + k]
                self.stack.append(msg_data)
                self.ip += 1
            except:
                print("[CALLDATALOAD] Smth went wrong with input :(")
                exit()
            
        #CALLDATASIZE
        elif command == 0x36:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                value = hex(int(len(self.data['msg_data']) / 2))[2:]
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
                msg_data_size = value
                self.stack.append(msg_data_size)
                self.ip += 1
            except:
                print("[CALLDATASIZE] Smth went wrong with input :(")
                exit()

        #CALLDATACOPY
        elif command == 0x37:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                destOffset = int(self.stack.pop(), 16)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)

                for k in range(0, length * 2):
                    memory[destOffset * 2 + k] = self.data['msg_data'][offset * 2 + k]

                self.memory += length
                self.ip += 1
            except:
                print("[CALLDATACOPY] Smth went wrong with input :(")
                exit()

        #CODESIZE
        elif command == 0x38:
            try:
                self.stack.append(len(self.bytecode))
                self.ip += 1
            except:
                print("[CODESIZE] Smth went wrong with input :(")
                exit()

        #CODECOPY
        elif command == 0x39:
            try:
                # Instruction where we can use our fuzzer!
                destOffset = int(self.stack.pop(), 16)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)

                for k in range(0, length):
                    memory[destOffset * 2 + k] = self.bytecode[offset + k]
                
                self.memory += length
                self.ip += 1
            except:
                print("[CODECOPY] Smth went wrong with input :(")
                exit()

        #GASPRICE
        elif command == 0x3a:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['tx_gasprice'])
                self.ip += 1
            except:
                print("[GASPRICE] Smth went wrong with input :(")
                exit()

        #EXTCODESIZE
        elif command == 0x3b:
            try:
                # Instruction where we can use our fuzzer!
                address = self.stack.pop()[24:64]
                r3 = requests.get('https://etherscan.io/address/0x' + address, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})

                i = r3.text.find('verifiedbytecode2') + 19
                k = r3.text[i:].find('<')
                ext_bytecode = r3.text[i:i + k]
                value = hex(len(ext_bytecode) / 2)[2:]
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
                ext_bytecode_len = value

                self.stack.append(ext_bytecode_len)
                self.ip += 1
            except:
                print("[EXTCODESIZE] Smth went wrong with input :(")
                exit()

        #EXTCODECOPY
        elif command == 0x3c:
            try:
                # Instruction where we can use our fuzzer!
                address = self.stack.pop()[24:64]
                destOffset = int(self.stack.pop(), 16)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)

                r3 = requests.get('https://etherscan.io/address/0x' + address, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})

                i = r3.text.find('verifiedbytecode2') + 19
                k = r3.text[i:].find('<')
                ext_bytecode = r3.text[i:i + k]

                for k in range(0, length):
                    memory[destOffset * 2 + k] = ext_bytecode[offset * 2 + k]

                self.memory += length
                self.ip += 1
            except:
                print("[EXTCODECOPY] Smth went wrong with input :(")
                exit()

        #RETURNDATASIZE *I have just copy-paste CALLDATASIZE implementation*
        elif command == 0x3d:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                value = hex(int(len(self.data['msg_data']) / 2))[2:]
                length = 64 - len(value)
                for k in range(0, length):
                    value = "0" + value
                msg_data_size = value
                self.stack.append(msg_data_size)
                self.ip += 1
            except:
                print("[RETURNDATASIZE] Smth went wrong with input :(")
                exit()

        #RETURNDATACOPY *I have just copy-paste CALLDATACOPY implementation*
        elif command == 0x3e: 
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()
                destOffset = int(self.stack.pop(), 16)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)

                for k in range(0, length * 2):
                    memory[destOffset * 2 + k] = self.data['msg_data'][offset * 2 + k]

                self.memory += length
                self.ip += 1
            except:
                print("[RETURNDATACOPY] Smth went wrong with input :(")
                exit()

        #EXTCODEHASH
        elif command == 0x3f: 
            try:
                # Instruction where we can use our fuzzer!
                address = self.stack.pop()[24:64]

                r3 = requests.get('https://etherscan.io/address/0x' + address, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})

                i = r3.text.find('verifiedbytecode2') + 19
                k = r3.text[i:].find('<')
                ext_bytecode = bytes.fromhex(r3.text[i:i + k])

                k = keccak.new(digest_bits=256)
                k.update(ext_bytecode)
                res = k.hexdigest()

                self.stack.append(hex(res)[2:])
                self.ip += 1
            except:
                print("[EXTCODEHASH] Smth went wrong with input :(")
                exit()

        #BLOCKHASH
        elif command == 0x40:
            try:
                # Instruction where we can use our fuzzer!
                blocknum = int(self.stack.pop(), 16)
                r2 = requests.get('https://etherscan.io/block/' + str(blocknum), headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:92.0) Gecko/20100101 Firefox/92.0"})
            
                i = r2.text.find('Hash:') + 37
                blockhash = r2.text[i:i + 64]

                self.stack.append(blockhash)
                self.ip += 1
            except:
                print("[BLOCKHASH] Smth went wrong with input :(")
                exit()

        #COINBASE
        elif command == 0x41:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['block_coinbase'])
                self.ip += 1
            except:
                print("[COINBASE] Smth went wrong with input :(")
                exit()

        #TIMESTAMP
        elif command == 0x42:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['block_timestamp'])
                self.ip += 1
            except:
                print("[TIMESTAMP] Smth went wrong with input :(")
                exit()

        #NUMBER
        elif command == 0x43:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['block_number'])
                self.ip += 1
            except:
                print("[NUMBER] Smth went wrong with input :(")
                exit()

        #DIFFICULTY
        elif command == 0x44:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['block_difficulty'])
                self.ip += 1
            except:
                print("[DIFFICULTY] Smth went wrong with input :(")
                exit()

        #GASLIMIT
        elif command == 0x45:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['block_gaslimit'])
                self.ip += 1
            except:
                print("[GASLIMIT] Smth went wrong with input :(")
                exit()

        #CHAINID
        elif command == 0x46:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['chain_id'])
                self.ip += 1
            except:
                print("[CHAINID] Smth went wrong with input :(")
                exit()

        #SELFBALANCE
        elif command == 0x47:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['this_balance'])
                self.ip += 1
            except:
                print("[SELFBALANCE] Smth went wrong with input :(")
                exit()

        #BASEFEE
        elif command == 0x48:
            try:
                # Instruction where we can use our fuzzer!
                if self.data == "0":
                    print("Emulation aborted. Request or override value for instruction: " + str(command))
                    exit()

                self.stack.append(self.data['base_fee'])
                self.ip += 1
            except:
                print("[BASEFEE] Smth went wrong with input :(")
                exit()

        #CREATE
        elif command == 0xf0:
            try:
                value = int(self.stack.pop(), 16)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)
                if (int(self.data['this_balance'], 16) - value) < 0:
                    return 0x1000
                if (int(self.data['this_balance'], 16) + value) > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    return 0x1001
                self.ip += 1
            except:
                print("[CREATE] Smth went wrong with input :(")
                exit()
        
        # A -> B -> C = storage = C
        #CALL
        elif command == 0xf1:
            try:
                gas = int(self.stack.pop(), 16)
                addr = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                argsOffset = int(self.stack.pop(), 16)
                argsLength = int(self.stack.pop(), 16)
                retOffset = int(self.stack.pop(), 16)
                retLength = int(self.stack.pop(), 16)
                if (int(self.data['this_balance'], 16) - value) < 0:
                    return 0x1000
                if (int(self.data['this_balance'], 16) + value) > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    return 0x1001
                self.ip += 1
            except:
                print("[CALL] Smth went wrong with input :(")
                exit()

        # A -> B -> C = (msg.sender, msg.value) C == B. storage = B
        #CALLCODE
        elif command == 0xf2:
            try:
                gas = int(self.stack.pop(), 16)
                addr = int(self.stack.pop(), 16)
                value = int(self.stack.pop(), 16)
                argsOffset = int(self.stack.pop(), 16)
                argsLength = int(self.stack.pop(), 16)
                retOffset = int(self.stack.pop(), 16)
                retLength = int(self.stack.pop(), 16)
                if (int(self.data['this_balance'], 16) - value) < 0:
                    return 0x1000
                if (int(self.data['this_balance'], 16) + value) > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    return 0x1001
                self.ip += 1
            except:
                print("[CALLCODE] Smth went wrong with input :(")
                exit()

        #RETURN
        elif command == 0xf3:
            try:
                # Returns data to blockchain. This opcode can lead to strange behaviour(i.e. deploy contract instead of values)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)
                return 0xf3
            except:
                print("[RETURN] Smth went wrong with input :(")
                exit()
        
        # A -> B -> C = (msg.sender, msg.value) C == A, storage = A
        #DELEGATECALL
        elif command == 0xf4:
            try:
                gas = int(self.stack.pop(), 16)
                addr = int(self.stack.pop(), 16)
                argsOffset = int(self.stack.pop(), 16)
                argsLength = int(self.stack.pop(), 16)
                retOffset = int(self.stack.pop(), 16)
                retLength = int(self.stack.pop(), 16)
                self.ip += 1
            except:
                print("[DELEGATECALL] Smth went wrong with input :(")
                exit()
        
        #CREATE2
        elif command == 0xf5:
            try:
                value = int(self.stack.pop(), 16)
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)
                salt = int(self.stack.pop(), 16)
                if (int(self.data['this_balance'], 16) - value) < 0:
                    return 0x1000
                if (int(self.data['this_balance'], 16) + value) > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    return 0x1001
                self.ip += 1
            except:
                print("[CREATE2] Smth went wrong with input :(")
                exit()

        # This allows contracts to make calls that are clearly non-state-changing
        #STATICCALL
        elif command == 0xfa:
            try:
                gas = int(self.stack.pop(), 16)
                addr = int(self.stack.pop(), 16)
                argsOffset = int(self.stack.pop(), 16)
                argsLength = int(self.stack.pop(), 16)
                retOffset = int(self.stack.pop(), 16)
                retLength = int(self.stack.pop(), 16)
                self.ip += 1
            except:
                print("[STATICCALL] Smth went wrong with input :(")
                exit()

        #REVERT
        elif command == 0xfd:
            try:
                offset = int(self.stack.pop(), 16)
                length = int(self.stack.pop(), 16)
                return 0xfd
            except:
                print("[REVERT] Smth went wrong with input :(")
                exit()

        #SELFDESTRUCT
        elif command == 0xff:
            try:
                addr = int(self.stack.pop(), 16)
            except:
                print("[SELFDESTRUCT] Smth went wrong with input :(")
                exit()

if __name__ == "__main__":
    GUI()
