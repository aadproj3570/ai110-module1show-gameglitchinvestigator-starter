# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the game it *looked* finished — title, difficulty selector, a guess box, Submit / New Game buttons, and a "Show hint" checkbox — but it fell apart as soon as I actually tried to play more than one round. Three concrete bugs stood out:

1. **You couldn't start a new game after finishing one.** I'd win (or run out of attempts), then click "New Game 🔁" to play again, and the game just stayed frozen on the game-over screen — clicking did nothing. I expected it to clear my old guesses, pick a fresh secret number, and let me play again. Instead it kept showing "You already won. Start a new game to play again," no matter how many times I clicked. The cause was that the New Game button reset the attempts and secret number but never set the game's status back to `"playing"`, so the code kept hitting `st.stop()` and bailing out.

2. **The "Show hint" toggle did nothing on its own.** After submitting a guess, the "Too High / Too Low" hint would show, but toggling the "Show hint" checkbox afterward had no effect — the hint wouldn't reliably hide or reappear unless I flipped it off *and* back on (or submitted another guess). I expected the hint to instantly appear/disappear based on the checkbox. The cause was that the hint was only drawn inside the "submit" block and was never saved to session state, so a plain checkbox rerun had nothing to redraw.

3. **Pressing Enter didn't count my guess.** I'd type a number and hit Enter (the natural thing to do), and nothing happened — no hint, attempts didn't change, the guess wasn't recorded. Only clicking the "Submit Guess 🚀" button worked. I expected Enter and the button to behave identically. The cause was that the input and button weren't wrapped in a form, so pressing Enter just reran the app without ever triggering the submit branch.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

Input Used:
1) Win or lose a round, then click "New Game 🔁"	
2) Submit a guess, then toggle "Show hint" off	
3) Type 40 and press Enter

Expected Behavior:	
1) Board resets, can play again	
2) Hint hides/shows immediately
3) Guess submitted, "Go HIGHER!" shown

Actual Behavior:
1) Stuck on game-over screen; clicking did nothing
2) Toggling did nothing unless flipped off+on or resubmitted
3) Nothing happened; only Submit button worked

Console Error / Output:
1) none (status never reset to "playing")
2) none (hint never stored in session state)
3) none (input/button not in a form)

## 2. How did you use AI as a teammate?

I used my AI coding assistant inside VS Code, attaching `app.py` and `logic_utils.py` so it could see how the UI and logic related to each other. I treated it like a debugging partner: I described the symptom I saw while playing, asked it to explain the underlying logic, then decided whether to accept its fix.

- **A suggestion that was correct:** For the "New Game does nothing" bug, the AI explained that Streamlit reruns the whole script every interaction and that the New Game handler reset the attempts and secret but never set `st.session_state.status` back to `"playing"`, so the early `st.stop()` guard kept firing. It suggested resetting `status` (and clearing `history`/hints) inside the handler. I verified this by ending a game, clicking New Game, and confirming the board actually reset with a fresh number and a working guess box.
- **A suggestion that was incorrect/misleading:** *(Replace with the real one you ran into.)* For the Enter-key bug, the AI first suggested just adding a `key=` to the `st.text_input` and reading its value on rerun. I tried it and Enter still didn't count the guess, because a bare text input rerun never triggers the submit branch. The fix that actually worked was wrapping the input and submit button in an `st.form` with a `form_submit_button`, so Enter and the button both commit the value in one run. I verified by typing a number, pressing Enter, and watching the attempt count go up.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed by reproducing the exact steps from my Bug Reproduction Log and confirming the behavior was now correct — for example, ending a game and clicking New Game to confirm the board actually reset, and pressing Enter to confirm the guess was counted. For the guessing logic I also leaned on `pytest`: the tests in `tests/test_game_logic.py` check that `check_guess(50, 50)` returns `"Win"`, `check_guess(60, 50)` returns `"Too High"`, and `check_guess(40, 50)` returns `"Too Low"`, which catches the "backwards hints" problem directly. Running `python -m pytest` and seeing those pass gave me confidence the high/low logic was correct independent of the UI. AI helped here by explaining what each test asserted and suggesting an extra edge-case test so I understood *why* a passing test meant the bug was gone, not just that the code "looked right."

---

## 4. What did you learn about Streamlit and state?

The biggest thing I learned is that Streamlit re-runs your *entire* Python script from top to bottom every single time you interact with the page — click a button, type in a box, toggle a checkbox. So normal variables don't "remember" anything; they're recreated from scratch on every run. The only way to keep information alive between runs is `st.session_state`, which is like a little dictionary that persists. I'd explain it to a friend like this: imagine the whole script is a recipe that gets re-cooked from the first step every time you touch anything, and `st.session_state` is the one notebook on the counter that you're allowed to keep notes in between cooks. Most of my bugs came from this — the hint vanished because it was never written to that notebook, and New Game broke because the "game over" note in the notebook was never erased.

---

## 5. Looking ahead: your developer habits

One habit I want to reuse is writing down a reproduction log *before* fixing anything — listing the exact input, what I expected, and what actually happened. It forced me to slow down and understand each bug instead of guessing, and it gave the AI clear, specific context to work from. One thing I'd do differently next time is test AI suggestions more skeptically and in smaller steps — a couple of times a fix "looked right" but didn't actually change the behavior, and I only caught it because I re-ran the exact reproduction steps. Overall, this project made me see AI-generated code as a confident first draft rather than a finished product: it can write something that runs and looks polished while still being subtly broken, so it's my job to play it, test it, and verify it before trusting it.
