import random
import streamlit as st

# FIX: Refactored core game logic out of app.py into logic_utils.py (with the
# AI's help) so it can be unit-tested with pytest independently of the UI.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

# Hint message shown for each outcome. Logic (check_guess) decides the outcome;
# the UI decides how to phrase it. "Too High" => the guess was above the secret
# => tell the player to go LOWER.
HINTS = {
    "Win": "🎉 Correct!",
    "Too High": "📈 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")

st.sidebar.header("Settings")

# Initialize session state variables at the start
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "Normal"

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_hint" not in st.session_state:
    st.session_state.last_hint = None

if "last_message" not in st.session_state:
    st.session_state.last_message = None

if "game_counter" not in st.session_state:
    st.session_state.game_counter = 0

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# Reset game if difficulty changes
if difficulty != st.session_state.current_difficulty:
    st.session_state.current_difficulty = difficulty
    st.session_state.attempts = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.last_hint = None
    st.session_state.last_message = None
    st.session_state.game_counter += 1
    low, high = get_range_for_difficulty(difficulty)
    st.session_state.secret = random.randint(low, high)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

# Input + Submit live inside a form so the "Submit Guess" button and the
# Enter key behave identically: both submit the currently typed value in one
# run. (Previously a plain button didn't reliably commit the freshly typed
# text, so the hint only appeared when you pressed Enter.)
if st.session_state.status == "playing":
    with st.form(
        key=f"guess_form_{difficulty}_{st.session_state.game_counter}",
        clear_on_submit=True,
    ):
        raw_guess = st.text_input("Enter your guess:")
        submit = st.form_submit_button("Submit Guess 🚀")
else:
    raw_guess = ""
    submit = False

# Controls outside the form (toggling/clicking them shouldn't submit a guess)
col1, col2 = st.columns(2)
with col1:
    if st.session_state.status == "playing":
        show_hint = st.checkbox("Show hint", value=True)
    else:
        show_hint = True
with col2:
    new_game = st.button("New Game 🔁")

# Handle new game button
# FIX: The original New Game handler reset attempts/secret but never reset
# `status` back to "playing", so the game-over guard kept firing and the board
# stayed locked. AI pointed out the missing status reset; resetting it here
# (plus history/hints) lets the player actually start a fresh game.
if new_game:
    st.session_state.attempts = 0
    low, high = get_range_for_difficulty(difficulty)
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.last_hint = None
    st.session_state.last_message = None
    st.session_state.game_counter += 1
    st.success("New game started.")
    st.rerun()

# PROCESS SUBMISSION
if submit and raw_guess.strip():
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.error(err)
    elif guess_int < low or guess_int > high:
        st.error(f"❌ Guess must be between {low} and {high}. Try again.")
    elif guess_int in st.session_state.history:
        # Already-guessed number: reject without spending an attempt
        st.error(
            f"🔁 You already guessed {guess_int}. "
            f"That number is taken — pick a different one!"
        )
    else:
        # Valid, new guess - process it
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome = check_guess(guess_int, st.session_state.secret)
        message = HINTS[outcome]

        # Store hint
        st.session_state.last_hint = message
        st.session_state.last_message = outcome

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # Check win condition
        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
        # Check loss condition
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"

        # Rerun so the prompt, attempts-left counter, and saved hint all refresh
        st.rerun()

# Show saved hint while the game is still playing
# FIX: The original code only drew the hint inside the submit branch, so
# toggling "Show hint" did nothing. We now persist the hint in session state
# (last_hint) and re-render it here based on the checkbox on every rerun.
if st.session_state.status == "playing":
    if show_hint and st.session_state.last_hint and st.session_state.last_message != "Win":
        st.warning(st.session_state.last_hint)
    if st.session_state.history:
        st.caption("Already guessed: " + ", ".join(str(g) for g in st.session_state.history))

# Display game over messages if game ended (no hints shown)
if st.session_state.status != "playing":
    st.divider()
    if st.session_state.status == "won":
        st.success(f"🎉 You won! The secret was {st.session_state.secret}. Final score: {st.session_state.score}")
        st.success("🏆 Click 'New Game' to play again!")
    else:
        st.error(f"❌ Out of attempts! The secret was {st.session_state.secret}. Final score: {st.session_state.score}")
        st.error("😢 Click 'New Game' to try again.")
