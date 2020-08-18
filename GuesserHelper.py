import tkinter as tk
from tkinter import messagebox
from random import randint
from math import ceil

def concat(*args, sep=", ")->str:
    retr:str = ""
    for arg in args:
        if isinstance(arg, (list,tuple)):
            for sub in arg:
                retr += sep + concat(sub, sep=sep)
        else:
            retr += sep + str(arg)
    return retr[len(sep):]

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master:tk.Frame = master
        self.possible:list = [] # List of all possible words (strings)
        self.allWords:list = [] # List of all not possible words (strings)
        self.known:list = []
        self.prevKnownNot:str = ""
        self.length:int = 0
        self.lettersUsed:dict = {}
        self.initMasterWidget()
        self.createMenuBar()
        self.createLetterFreqWidget()
        self.createKnownWidget()
        self.createWordsWidget()

    def initMasterWidget(self):
        self.master.title("Word Guesser Helper")
        self.master.option_add("*Font", "Consolas 12")
        self.master.iconbitmap("Assets/Icon.ico")
        self.master.resizable(False, False)
        self.pack(padx=10, pady=10)

    def createMenuBar(self):
        self.menu_bar:tk.Menu = tk.Menu(self)
        self.master["menu"] = self.menu_bar
        self.menu_new:tk.Menu = tk.Menu(self.menu_bar, tearoff=0)
        # Any file named Words#.txt can be used
        # We just check for files of words of length 5->9, that can change
        for i in range(3, 11):
            f = None
            try: f = open("WordLists/Words"+str(i)+".txt")
            except FileNotFoundError: continue
            f.close()
            self.menu_new.add_command(
                label="Start "+str(i)+" letter word",
                command=lambda i=i:self.startWord(i)
            )
        self.menu_bar.add_cascade(menu=self.menu_new, label="New")

    def createLetterFreqWidget(self):
        self.frame_letters:tk.Frame = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)
        self.frame_letters.grid(row=0, column=0, padx=10, pady=10)
        self.label_letters:tk.Label = tk.Label(self.frame_letters,
            height=4,  justify=tk.CENTER,
            padx=10, pady=10,
            text="Letter Frequency\n1st\t*\t000\n2nd\t*\t000\n3rd\t*\t000"
        )
        self.label_letters.grid(sticky="NSEW")

    def createKnownWidget(self):
        self.frame_known:tk.Frame = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)
        self.frame_known.grid  (row=0, column=1, padx=10, pady=10)
        self.frame_knownLetters:tk.Frame = tk.Frame(self.frame_known)
        self.frame_knownLetters.grid(padx=10, pady=10)
        self.frame_knownNot:tk.Frame = tk.Frame(self.frame_known)
        self.frame_knownNot.grid(row=1, padx=10, pady=10)
        self.label_knownNot:tk.Label = tk.Label(self.frame_knownNot, height=1, justify=tk.RIGHT, text="None:")
        self.label_knownNot.pack(side=tk.LEFT)
        self.entries_letters:list = [] # the entries for each letter
        self.strings_letters:list = [] # the StringVars for each entry
        self.string_knownNot = tk.StringVar() # StringVar for the letters we know aren't in it
        self.entry_knownNot:tk.Entry = None # Entry for ^
        self.createEntries(6) # Just make 6 and disable them for visuals
        for i in range(6): self.entries_letters[i]["state"] = tk.DISABLED
        self.entry_knownNot["state"] = tk.DISABLED
        
    def createWordsWidget(self):
        self.frame_words = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)
        self.frame_words.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        self.label_words = tk.Label(self.frame_words,
            height=5, justify=tk.CENTER,
            padx=10, pady=10, wraplength=512, # 512 is good estimate
            text="Possible Words\n~~~~\t~~~~\n~~~~\t~~~~\n~~~~\t~~~~\n~~~~\t ..."
        )
        self.label_words.grid(sticky="NSEW")

    def createEntries(self, num:int):
        # Clean up
        for ent in self.entries_letters: ent.destroy()
        self.entries_letters.clear()
        self.strings_letters.clear()
        # Create our knownNot stuff
        self.string_knownNot = tk.StringVar()
        self.string_knownNot.trace_add("write",
            lambda name,index,mode:self.handleEntryUpdate(-1)
        )
        if self.entry_knownNot: self.entry_knownNot.destroy()
        self.entry_knownNot:tk.Entry = tk.Entry(self.frame_knownNot,
            width=14, textvariable=self.string_knownNot
        )
        self.entry_knownNot.pack(side=tk.LEFT, fill=tk.X)
        # Create each of our letter entries/stringvars
        for i in range(num):
            s = tk.StringVar()
            s.trace_add("write",
                lambda name,index,mode,i=i:self.handleEntryUpdate(i)
            )
            self.strings_letters.append(s)
            ent = tk.Entry(self.frame_knownLetters,
                width=2,    justify=tk.CENTER,
                textvariable=self.strings_letters[i]
            )
            ent.grid(row=0, column=i, padx=5, pady=10)
            self.entries_letters.append(ent)

    def initLettersUsed(self):
        self.lettersUsed.clear()
        for l in "abcdefghijklmnopqrstuvwxyz":
            self.lettersUsed[l] = False

    def startWord(self, _l:int):
        # Read all the words from the appropriate file
        _ls:str = str(_l)
        f = None
        try: f = open("WordLists/Words"+_ls+".txt")
        except FileNotFoundError:
            messagebox.showerror("Error: File not found",
                "File containing all words of length ("+_ls+") was not found.\n"+
                "It should be here: <programFolder>/WordLists/Words"+_ls+".txt"
            )
            return
        if not f.readable():
            messagebox.showerror("Error: File not readable",
                "File is protected for one reason or another.\n"+
                "Is the program installed on an external device?"
            )
            return
        self.allWords = f.readlines()
        f.close()
        # Init now, as file could've failed
        self.length = _l
        self.createEntries(self.length)
        self.known = ["*"] * self.length
        self.initLettersUsed()
        # Validate all the read words
        for i in range(len(self.allWords)-1, -1, -1):
            newWord:str = ""
            for letter in self.allWords[i]:
                if letter.isalpha():
                    newWord += letter
            if len(newWord)==self.length:
                self.allWords[i] = newWord
            else:
                self.allWords.pop(i)
        # Start off our outputs
        self.possible = self.allWords.copy()
        self.displayPossible()
        self.updateGuess()

    def updatePossible(self):
        # Slow but robust, will optimize later
        # Tried doing it first but realized there's  
        # more case intersection than ya think
        self.possible.clear()
        def matches(w:str):
            for i in range(self.length):
                if self.known[i] != "*":
                    if w[i] != self.known[i]:
                        return False
                else:
                    if self.lettersUsed[w[i]]:
                        return False
            return True
        for word in self.allWords:
            if matches(word):
                self.possible.append(word)

    def displayPossible(self):
        if len(self.possible)>=1:
            SEPERATOR = "    "
            getWordsPerLine = lambda _length : round(38 / (_length + 1.7))
            wordsPerLine:int = getWordsPerLine(self.length)
            wordsCount:int = wordsPerLine * 4 - 1
            s:str = "Possible Words"
            if len(self.possible) > wordsCount:
                # We cant display all words, so display a sample
                words:list = [""] * (wordsCount + 1)
                interval:int = int(len(self.possible) / wordsCount)
                for i in range(wordsCount):
                    j:int = interval*i + randint(0, interval-1)
                    words[i] = self.possible[j]
                words[wordsCount] = " "*(self.length-3) + "..."
                for line in range(4):
                    s += "\n" + concat(words[
                            line*wordsPerLine : (line+1)*wordsPerLine
                        ], sep=SEPERATOR
                    )
            else:
                # We can display all words, so do that
                linesUsed = ceil(len(self.possible) / wordsPerLine)
                s += "\n" * (5 - linesUsed)
                for line in range(linesUsed-1):
                    s += concat(self.possible[
                            line*wordsPerLine : (line+1)*wordsPerLine
                        ], sep=SEPERATOR
                    ) + "\n"
                s += concat(self.possible[
                        (linesUsed-1)*wordsPerLine :
                    ], sep=SEPERATOR
                )
            self.label_words["text"] = s
        else:
            self.label_words["text"] = "Possible Words\n\nNone!\n\n"

    def updateGuess(self):
        freqList:list = [0] * 26 # list of the frequency each letter, in lex order
        for word in self.possible:
            for letter in word:
                if not self.lettersUsed[letter]:
                    freqList[ord(letter)-97] += 1
        first=0; second=0; third=0 # the freq value of _
        first_i=0; second_i=0; third_i=0 # the index of that value in the list
        for index, freq in enumerate(freqList):
            if freq >= 0:
                if freq > third:
                    if freq > second:
                        if freq > first:
                            first = freq
                            first_i = index
                        else:
                            second = freq
                            second_i = index
                    else:
                        third = freq
                        third_i = index
                freqList[index] = 0
        # Fancy format display
        self.label_letters["text"] = "Letter Frequency\n1st\t{}\t{:>4}\n2nd\t{}\t{:>4}\n3rd\t{}\t{:>4}".format(
            chr(97+first_i),   first,   chr(97+second_i),   second,   chr(97+third_i),   third
        )

    def handleEntryUpdate(self, num:int):
        if num >= 0:
            # Updated known letter at position `num`
            s:str = self.strings_letters[num].get()
            c:str = s[-1].lower() if s else ""
            prev:str = self.known[num]
            if c.isalpha():
                self.known[num] = c
                self.lettersUsed[c] = True
                self.strings_letters[num].set(c)
            else:
                self.known[num] = "*"
                self.strings_letters[num].set("")
            if prev == self.known[num]:
                # nothing changed, dont update anything
                return
            if prev != "*":
                try: self.known.index(prev)
                except ValueError: self.lettersUsed[prev] = False
        else:
            # Updated letters that are known to NOT be in the word
            # Any number of letters could've been removed or added. fun
            s:str = self.string_knownNot.get()
            if self.prevKnownNot != s:
                newKnownNot:str = ""
                # Seperate letters that were removed or are still in the string
                for letter in self.prevKnownNot:
                    if s.find(letter) < 0:
                        self.lettersUsed[letter] = False
                    else:
                        newKnownNot += letter
                # Find letters that are newly added and are valid
                for letter in s:
                    if  letter.isalpha() \
                    and self.prevKnownNot.find(letter) < 0 \
                    and not self.lettersUsed[letter]:
                        l = letter.lower()
                        newKnownNot += l
                        self.lettersUsed[l] = True
                # newKnownNot was calc. in the two for loops (og - removed + added)
                if self.prevKnownNot == newKnownNot:
                    # nothing changed, dont update anything
                    self.string_knownNot.set(self.prevKnownNot)
                    return
                self.prevKnownNot = newKnownNot
                self.string_knownNot.set(self.prevKnownNot)  
        # Update all our stuff. Can bind to a button aswell if ya like
        self.updatePossible()
        self.displayPossible()
        self.updateGuess()


    
root = tk.Tk()
app = Application(master=root)
app.mainloop()
