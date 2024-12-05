import streamlit as st
import sqlite3
from datetime import datetime
import os
import random
import streamlit.components.v1 as components


# Database Setup
def init_db():
    """Initialize the SQLite database for journaling"""
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mood TEXT,
            entry_type TEXT,
            content TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Database Operations
def add_journal_entry(entry_type, content, mood=None):
    """Add a new journal entry to the database"""
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    c.execute('''
        INSERT INTO entries (date, mood, entry_type, content) 
        VALUES (?, ?, ?, ?)
    ''', (date, mood, entry_type, content))

    conn.commit()
    conn.close()


def get_journal_entries(filter_type=None, start_date=None, end_date=None):
    """Retrieve journal entries with optional filtering"""
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()

    query = "SELECT * FROM entries WHERE 1=1"
    params = []

    if filter_type:
        query += " AND entry_type = ?"
        params.append(filter_type)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    c.execute(query, params)
    entries = c.fetchall()
    conn.close()

    return entries


# Daily Prompts
def get_daily_prompt():
    """Generate a daily journaling prompt"""
    prompts = [
        "What are you grateful for today?",
        "Describe a moment that made you smile today.",
        "What challenge did you overcome recently?",
        "Write about something you learned today.",
        "How are you feeling right now, and why?"
    ]
    return random.choice(prompts)


def get_additional_prompts():
    """Generate additional journaling prompts based on user input"""
    additional_prompts = [
        "Can you elaborate more on that?",
        "How did that make you feel?",
        "What did you learn from this experience?",
        "What would you do differently next time?",
        "How has this impacted your day?"
    ]
    return random.choice(additional_prompts)


# Streamlit App
def main():
    # Initialize database
    init_db()

    st.title("Personal Journal")

    # Headline and Brief Description
    st.header("Welcome to Your Personal Journal")
    st.write(
        "This app helps you reflect on your day by providing prompts and summarizing your entries. You can also track your mood and gain insights over time.")

    # Sidebar Navigation
    menu = st.sidebar.selectbox("Menu",
                                ["Write Entry", "View Entries", "Mood Tracker"]
                                )

    if menu == "Write Entry":
        write_entry_page()
    elif menu == "View Entries":
        view_entries_page()
    elif menu == "Mood Tracker":
        mood_tracker_page()


def write_entry_page():
    st.header("New Journal Entry")
    # Mood Selection using icons and scale for sub-emotions

    st.write("Select your current emotion:")

    mood = None  # Initialize mood variable
    sub_mood = None  # Initialize sub_mood variable

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("😊 Happy"):
            mood = "Happy"
            sub_mood = st.slider("Intensity", 1, 10)

    with col2:
        if st.button("😢 Sad"):
            mood = "Sad"
            sub_mood = st.slider("Intensity", 1, 10)

    with col3:
        if st.button("😡 Angry"):
            mood = "Angry"
            sub_mood = st.slider("Intensity", 1, 10)

    with col4:
        if st.button("😨 Fearful"):
            mood = "Fearful"
            sub_mood = st.slider("Intensity", 1, 10)

    # Daily Prompt with button to generate new prompt
    prompt = st.empty()
    prompt_text = get_daily_prompt()

    def update_prompt():
        nonlocal prompt_text
        prompt_text = get_daily_prompt()
        prompt.write("Let's write about: " + prompt_text)

    update_prompt()

    if st.button("New Idea"):
        update_prompt()

    # Entry Type Selection
    entry_type = st.selectbox("Entry Type",
                              ["Text", "Reflection", "Goals", "Thoughts"]
                              )


    # Text Entry with additional prompts based on input
    content = st.text_area("Write your entry here...")

    if content.strip():
        additional_prompt = get_additional_prompts()
        st.write("Additional Prompt: " + additional_prompt)

    # Icons to add pictures and narrate as audio (dummy icons)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🖼️ Add Picture"):
            st.write("Picture added (dummy)")

    with col2:
        if st.button("🎤 Narrate as Audio"):
            st.write("Audio transcribed (dummy)")

    # Save Button
    if st.button("Save Entry"):
        if content.strip() and mood is not None and sub_mood is not None:
            add_journal_entry(entry_type, content, f"{mood} (Intensity: {sub_mood})")
            st.success("Entry saved successfully!")
        else:
            st.warning("Please write something and select an emotion before saving.")


def view_entries_page():
    st.header("Your Journal Entries")

    # Filtering Options
    col1, col2 = st.columns(2)

    with col1:
        filter_type = st.selectbox("Filter by Type",
                                   ["All", "Text", "Reflection", "Goals", "Thoughts"]
                                   )

    with col2:
        date_filter = st.date_input("Filter by Date Range",
                                    value=None, key="date_range"
                                    )

    # Retrieve and Display Entries
    if filter_type == "All":
        filter_type = None

    entries = get_journal_entries(filter_type)

    for entry in entries:
        st.write(f"Date: {entry[1]}")
        st.write(f"Type: {entry[3]}")
        st.write(f"Mood: {entry[2]}")
        st.write(entry[4])
        st.markdown("---")


def mood_tracker_page():
    st.header("Mood Tracking")

    # Mood Distribution
    mood_counts = {}
    entries = get_journal_entries()
    for entry in entries:
        mood = entry[2]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    st.bar_chart(mood_counts)

    # Recent Mood Trends
    st.subheader("Recent Mood Trends")
    recent_entries = entries[-5:]  # Last 5 entries
    for entry in recent_entries:
        st.write(f"{entry[1]}: {entry[2]}")


if __name__ == "__main__":
    main()