import streamlit as st

# In a real-world application, you would use a database and secure password storage
# Here, we're using a simple dictionary for demonstration purposes
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

def authenticate(username, password):
    if username in users and users[username]["password"] == password:
        return users[username]["role"]
    return None

def login():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state["username"] = username
            st.session_state["role"] = role
            return True
        else:
            st.sidebar.error("Invalid username or password")
            return False
    return False

def logout():
    st.session_state.pop("username", None)
    st.session_state.pop("role", None)
    st.sidebar.success("Logged out successfully")

def is_authenticated():
    return "username" in st.session_state and "role" in st.session_state

def get_current_user():
    return st.session_state.get("username", None)

def change_password(username, new_password):
    if username in users:
        users[username]["password"] = new_password
        return True
    return False
