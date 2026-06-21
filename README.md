# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Purpose:** A Streamlit number-guessing game. The app picks a secret number within a range that depends on the chosen difficulty (Easy 1–20, Normal 1–100, Hard 1–50), and the player guesses until they find it or run out of attempts, getting "Too High / Too Low" hints and a running score.
- [x] **Bugs found:**
  1. Clicking "New Game" after winning/losing didn't restart the game — it stayed locked on the game-over screen (the status was never reset to `"playing"`).
  2. The "Show hint" checkbox did nothing on its own; the hint only updated when you submitted again or toggled it off and back on (the hint was never saved to session state).
  3. Pressing Enter in the guess box didn't register a guess — only the "Submit Guess" button worked (the input wasn't inside a form).
- [x] **Fixes applied:** Reset `st.session_state.status` (and `history`/hints) inside the New Game handler; store the latest hint in `st.session_state.last_hint` and render it from session state based on the checkbox; wrap the input and submit button in an `st.form` so Enter and the button both submit a guess.

## 📸 Demo Walkthrough

A sample game on **Normal** difficulty (secret number is between 1 and 100):

1. User selects **Normal** difficulty in the sidebar and reads "Guess a number between 1 and 100."
2. User enters a guess of **40** → game responds **"Go HIGHER!"** (Too Low).
3. User enters a guess of **70** → game responds **"Go LOWER!"** (Too High).
4. The "Already guessed" list and attempts-left counter update after each guess, and the score updates correctly.
5. User enters **63** (the secret) → game shows **"🎉 You won!"**, fires balloons, reveals the secret, and shows the final score.
6. User clicks **"New Game 🔁"** → the board resets with a fresh secret number and the player can play again.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ python -m pytest tests/
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
collected 6 items

tests\test_game_logic.py ......                                          [100%]

============================== 6 passed in 0.06s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
