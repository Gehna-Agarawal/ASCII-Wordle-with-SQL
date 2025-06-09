import csv
import random
import time
import blessed
import pyperclip
import text
import mysql.connector
from mysql.connector import Error

term = blessed.Terminal()
letterDict = text.lettersDict

class Database:
    '''Handles MySQL connection, user login, and streaks.'''

    def __init__(self):
        self.connection = self.connect_db()
        self.user_data = None

    def connect_db(self):
        '''Establishes the database connection.'''
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Gehna@100",
                database="wordle_game"
            )
            if connection.is_connected():
                print("Connected to MySQL database.")
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            exit(1)

    def register_user(self, username, password):
        '''Registers a new user in the database.'''
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.connection.commit()
            print("Registration successful!")
            self.user_data = {"username": username, "longest_streak": 0, "current_streak": 0}
        except Error as e:
            print(f"Registration failed: {e}")

    def login_user(self, username, password):
        '''Logs in the user by verifying credentials.'''
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            if user:
                print("Login successful!")
                self.user_data = user
            else:
                print("Invalid username or password.")
        except Error as e:
            print(f"Login failed: {e}")

    def update_streaks(self, won):
        '''Updates the streak values based on the game result.'''
        if self.user_data:
            # Calculate new current and longest streaks based on win/loss
            new_current_streak = self.user_data['current_streak'] + 1 if won else 0
            new_longest_streak = max(self.user_data['longest_streak'], new_current_streak)

            # Update the database with the new streak values
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE users SET current_streak=%s, longest_streak=%s WHERE username=%s",
                (new_current_streak, new_longest_streak, self.user_data['username'])
            )
            self.connection.commit()

            # Update local user data to reflect new streak values
            self.user_data['current_streak'] = new_current_streak
            self.user_data['longest_streak'] = new_longest_streak

class Box:
    '''A class to handle the drawing of 20x10 ASCII Boxes'''
    def __init__(self, loc: list):
        self.loc = loc

    def draw(self, color: str, sleep: float = 0) -> None:
        '''Draws a box of color "color"'''
        print(color, end='')
        for i in range(10):
            print(f'{term.move_xy(self.loc[0], self.loc[1] + i)}{"█" * 20}')
            time.sleep(sleep)
        print(term.normal, end='', flush=True)

class Wordle:
    '''Class that handles game logic for ASCII Wordle'''
    def __init__(self, db):
        self.secretWord = ""
        self.wordList = set()
        self.db = db
        try:
            with open('wordList.csv', 'r') as csvFile:
                reader = csv.reader(csvFile)
                words = [row[0] for row in reader]
                self.secretWord = random.choice(words)
                self.wordList = set(words)
        except Exception as e:
            print(f"Error reading word list: {e}")
            exit(1)
        self.count = self.generateCount()
        self.corrects = []
        self.curRow = 0

    def setup(self) -> None:
        '''Sets up the game screen, ensuring alignment of grid and boxes'''
        input('Maximize your window, set the font size low enough. Press enter to start!')
        print(term.clear)
        self.drawWords('WORDLE', (term.width // 2 -30 , 5), term.white)
        self.drawStreaks()
        
        grid_width = 5 * 21  # Width for 5 boxes with 20 characters each + 1 space
        grid_height = 6 * 11  # Height for 6 rows of boxes each with 10 characters + 1 space
        start_x = (term.width - grid_width) // 2
        start_y = (term.height - grid_height) // 2

        # Define grid of box objects, positioning them centrally on the screen
        self.boxGrid = [[Box([start_x + 21 * i, start_y + 11 * j]) for i in range(5)] for j in range(6)]
        
        # Draw the canvas/grid on screen
        self.drawCanvas()

    def drawStreaks(self):
        '''Displays the streaks at the top of the screen.'''
        if self.db.user_data:
            longest = self.db.user_data["longest_streak"]
            current = self.db.user_data["current_streak"]
            
            # Format the streak text with current values
            streak_text = f"Longest Streak: {longest} | Current Streak: {current}"
            
            # Calculate the x position to center streak text
            center_x = (term.width // 2) - (len(streak_text) * 4)
            
            # Set y position to leave space under title, adjust if necessary
            center_y = 20
            
            # Draw streak information in the center
            self.drawWords(streak_text, (center_x, center_y), term.yellow)


    def drawCanvas(self) -> None:
        '''Draws all 6 rows of boxes on screen'''

        for i in self.boxGrid:
            for j in i:
                j.draw(color=term.grey8)

    def drawLetterBox(self, letter: list, gridVal: tuple, color: str) -> None:
        '''Draws a centered letter within the specified box location'''
        for col, rowChar in enumerate(letter):
            for row, char in enumerate(rowChar):
                if char != ' ':
                    print(f'{term.normal}{term.move_xy(gridVal[0] + row, gridVal[1] + col)}{char}', end='', flush=True)
                else:
                    print(f'{color}{term.move_xy(gridVal[0] + row, gridVal[1] + col)}{"█"}', end='', flush=True)

    def drawWords(self, word: str, startPos: tuple, color: str) -> None:
        '''Allows for the drawing of entire words on screen'''

        print(color)

        for col, rowChar in enumerate(word):
            for index, rowChar in enumerate(letterDict[rowChar.upper()].split('\n')):
                print(f'{term.move_xy(startPos[0] + 10 * col, startPos[1] + index)}{rowChar}')

        print(term.normal)


    def generateCount(self) -> dict:
        '''Generates a dictionary containing the count of each unique character in secretWord'''

        count = dict()
        for i in self.secretWord:
            if i not in count:
                count[i] = 1
            else:
                count[i] += 1

        return count

    def evaluateInput(self, guess: str) -> None:
        '''Checks the user's guess's validity against the secretWord'''

        for index, char in enumerate(guess):
            if char == self.secretWord[index] and self.loopCount[char] > 0:
                self.boxGrid[self.curRow][index].draw(color=term.chartreuse3, sleep=0.01)
                self.drawLetterBox(letterDict[char].split('\n'), calculatePos(index, self.curRow), color=term.chartreuse3)
                self.loopCount[char] -= 1
                self.corrects[self.curRow] += '🟩'

            elif char in self.secretWord and self.loopCount[char] > 0:
                self.boxGrid[self.curRow][index].draw(color=term.gold2, sleep=0.01)
                self.drawLetterBox(letterDict[char].split('\n'), calculatePos(index, self.curRow), color=term.gold2)
                self.loopCount[char] -= 1
                self.corrects[self.curRow] += '🟨'

            else:
                self.boxGrid[self.curRow][index].draw(color=term.grey23, sleep=0.01)
                self.drawLetterBox(letterDict[char].split('\n'), calculatePos(index, self.curRow), color=term.grey23)
                self.corrects[self.curRow] += '⬛'

    def removeLetter(self, inputArr: list) -> None:
        '''Removes most recently drawn letter by drawing its corresponding box over it'''

        inputArr[0: len(inputArr)] = inputArr[0:5]

        if len(inputArr) > 0:
            self.boxGrid[self.curRow][len(inputArr) - 1].draw(term.grey8)
            inputArr.pop()

    def evaluateError(self, key: str) -> str:
        '''Evaluates user input for input size errors or invalid words'''

        if len(self.inputArr) < 5:
            self.drawWords('NOTENOUGHLETTERS', (160, 100), term.white)
            return ''

        elif ''.join(self.inputArr) not in self.wordList:
            self.drawWords('NOTINWORDLIST', (170, 100), term.white)
            key = ''
            return ''

        return key

    def gameLoop(self) -> None:
        '''Starts the main game loop'''

        while self.curRow <= 5:
            self.corrects.append('')
            self.loopCount = self.count.copy()

            with term.cbreak():
                key = ''
                self.inputArr = []

                while repr(key) != 'KEY_ENTER':
                    key = term.inkey()
                    keyName = (key.name if key.is_sequence else key).upper()

                    if keyName == 'KEY_ENTER':
                        self.drawWords('################', (160, 100), term.black)
                        key = self.evaluateError(key)
                        continue

                    elif keyName == 'KEY_BACKSPACE':
                        self.removeLetter(self.inputArr)
                        continue

                    elif keyName in letterDict:
                        self.inputArr.append(keyName)
                        self.drawLetterBox(
                            letterDict[keyName].split('\n'),
                            calculatePos(len(self.inputArr[0:5]) - 1, self.curRow),
                            color=term.grey8)
                        continue

            guess = ''.join(self.inputArr)[0:5].upper() # Ensure the guess is in uppercase
            self.evaluateInput(guess)

            if self.corrects[self.curRow].count('🟩') == 5:
                break

            self.curRow += 1

        self.gameEnd()

    def gameEnd(self) -> None:
        '''Ends the game, updates streaks, and displays remarks.'''

        # Check if the user won
        won = self.curRow < len(self.corrects) and self.corrects[self.curRow].count('🟩') == 5

        # Update streaks in the database based on the game result
        self.db.update_streaks(won)

        # Determine and display end-game remark
        winRemark = ['GENIUS', 'MAGNIFICENT', 'IMPRESSIVE', 'SPLENDID', 'GREAT', 'PHEW']
        remark = winRemark[self.curRow] if won else self.secretWord  # Show the word if player loses
        
        # Center remark horizontally
        remark_x = (term.width - len(remark) * 10) // 2
        self.drawWords(remark, (remark_x, 120), term.white)

        # Copy the result to the clipboard for convenience
        pyperclip.copy(f"Wordle {self.curRow}/6{chr(10)}{chr(10).join(self.corrects)}")
        input()  # Prevents program from closing upon completion

def calculatePos(row: int, col: int) -> tuple:
    '''Calculates the adjusted centered position for each letter in the box, with slight offsets.'''
    grid_width = 5 * 21  # Width for 5 boxes with 20 characters each + 1 space
    grid_height = 6 * 11  # Height for 6 rows of boxes each with 10 characters + 1 space
    start_x = (term.width - grid_width) // 2
    start_y = (term.height - grid_height) // 2
    # Calculate row and column positions with additional offsets
    return (start_x + row * 21 + 5, start_y + col * 11 + 1)


def main() -> None:
    '''Handles user login and starts the game loop'''
    db = Database()
    
    while True:
        mode = input("Enter '1' to play as Guest, '2' to Login, '3' to Register: ")
        
        if mode == '1':
            print("Playing as Guest...")
            break  # Proceed without login

        elif mode == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            db.login_user(username, password)
            
            if db.user_data:
                break  # Exit loop if login is successful
            else:
                print("Incorrect username or password. Please try again.\n")
        
        elif mode == '3':
            username = input("Create username: ")
            password = input("Create password: ")
            db.register_user(username, password)
            
            if db.user_data:
                break  # Exit loop after successful registration
        else:
            print("Invalid selection. Please enter '1', '2', or '3'.\n")
    
    game = Wordle(db)
    game.setup()
    game.gameLoop()

main()
