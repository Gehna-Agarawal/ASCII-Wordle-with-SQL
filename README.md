# 🟩 ASCII Wordle Game (Terminal Version with MySQL)

A visually rich, terminal-based **Wordle clone** implemented in Python using ASCII art, complete with user login, registration, and streak tracking via a **MySQL database**.

---

## 🎮 Features

- **Guest & Registered Play Modes**  
  Play anonymously or register/login to track your streaks.  

- **Full ASCII Art Display**  
  Beautiful terminal rendering of boxes and letters using the `blessed` library.

- **MySQL Integration**  
  Store user credentials, current streak, and longest streak securely.

- **Game Result Sharing**  
  Automatically copies your results to clipboard (like the original Wordle).

- **Cross-platform Terminal Experience**  
  Runs on Windows, Linux, and macOS (in compatible terminals).

---

## 🖥️ Screenshots
![Screenshot 2025-06-09 125428](https://github.com/user-attachments/assets/8d21dfa0-1782-4a52-b42c-a0e6e539d933)


---

## 📦 Requirements

- Python 3.8+
- MySQL server running locally
- Python packages:
  - `blessed`
  - `pyperclip`
  - `mysql-connector-python`
    
 ---
 
 ## Install dependencies:
 ```cmd
pip install blessed pyperclip mysql-connector-python
```

---

## 🗃️ Setup Instructions
**1. Clone the Repository**
 ```cmd
git clone https://github.com/Gehna-Agarawal/ASCII-Wordle-with-SQL.git
cd ASCII-Wordle-with-SQL
```

**2. Create the MySQL Database**
Run this SQL in your MySQL shell or via a tool like phpMyAdmin:
```sql
CREATE DATABASE wordle_game;
USE wordle_game;
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOTNULL,
    longest_streak INT DEFAULT 0,
    current_streak INT DEFAULT 0
);

```
**3. Prepare Supporting Files**
Ensure the following files are present:
  - `text.py` – contains `lettersDict` for ASCII letter rendering
  - `wordList.csv` – CSV with a list of valid 5-letter words

If not present, create them or download from this repo.

---

##🚀 Run the Game
```
python wordle.py
```
(You may rename the main game script to `main.py` if needed.)

---

## ✍️ How to Play
- Make sure you have zoomed out enough, else the game will look like a garbled mess
- Type one letter at a time.
- Press Enter to submit your 5-letter guess.
- Use Backspace to delete.
- Colours follow standard Wordle rules:
  - 🟩 Correct letter and position
  - 🟨 Correct letter, wrong position
  - ⬛ Letter not in word

---

## 📌 Notes
- Resize your terminal window and use a small font size for best visuals.
- You can play as a guest without storing streaks.
- Streak data is saved only for registered users.

---
## 🙋‍♀️ Author
Made with 💚 by Gehna Agarawal
Feel free to fork this project
