import random
import streamlit as st

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📈 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

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

        outcome, message = check_guess(guess_int, st.session_state.secret)

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
