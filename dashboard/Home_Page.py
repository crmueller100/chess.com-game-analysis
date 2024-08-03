import streamlit as st

st.set_page_config(
    page_title="Chess Analysis",
    page_icon=":chess_pawn:",
    layout="wide"
)
st.title("Welcome to my Chess Analysis Dashboard!")  # More prominent title

st.sidebar.success("Select a dashboard above.")

st.markdown(
    """
    This interactive dashboard empowers you to dive into your [chess.com](https://chess.com/) game history, providing a comprehensive analysis of your performance.
    
    **Key Features:**

    * **Personal Stats:** Gain insights into your personal performance and game outcomes.
    * **Compare With Others:** Benchmark your skills against other players, including grandmasters.
    * **Track Your Progress:** Visualize your rating trends and improvement over time.
    * **Discover Your Strengths and Weaknesses:** Identify patterns in your openings, tactics, and endgames.

    To get started, navigate through the dashboards using the sidebar on the left.

    This app is powered by [Streamlit](https://streamlit.io/) and the [chess.com API](https://www.chess.com/news/view/published-data-api).
    """
)
