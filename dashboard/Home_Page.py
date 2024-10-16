import streamlit as st

st.set_page_config(
    page_title="Chess Analysis",
    page_icon=":chess_pawn:",
    layout="wide"
)
st.title("Welcome to my Chess Analysis Dashboard!")

st.sidebar.success("Select a dashboard above.")

st.markdown(
    """
    This interactive dashboard empowers you to dive into your [chess.com](https://chess.com/) game history, providing a comprehensive analysis of your performance.
    
    Select from any of **3 Dashboards** to explore:

    * **Personal Stats:** Uncover insights into your personal performance and track your progress over time.
    * **Game Explorer:** Browse all games stored in the local database. 
    * **Stockfish Analysis:** Want a deep dive into your games? Pull the `game_id` from the Game Explorer, submit it to an Airflow job, and run a Stockfish analysis on your game.

    To get started, navigate to each dashboard using the sidebar on the left.

    This dashboard is powered by [Streamlit](https://streamlit.io/). The game data is from [chess.com API](https://www.chess.com/news/view/published-data-api).
    """
)
