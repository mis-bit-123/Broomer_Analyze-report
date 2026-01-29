import streamlit as st
import hashlib
from config_loader import USERS, DASHBOARD_CONFIG


class Authenticator:
    def __init__(self):
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_credentials(self, username, password):
        if username in USERS:
            stored = self.hash_password(USERS[username]['password'])
            return stored == self.hash_password(password)
        return False
    
    def login(self):
        if not st.session_state.authenticated:
            st.title(f"{DASHBOARD_CONFIG['logo']} {DASHBOARD_CONFIG['title']}")
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.subheader("🔐 Secure Login")
                
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login")
                
                if submit:
                    if self.check_credentials(username, password):
                        st.session_state.authenticated = True
                        st.session_state.user = username
                        st.session_state.user_name = USERS[username]['name']
                        st.session_state.role = USERS[username]['role']
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                
                with st.expander("👤 Demo Credentials"):
                    for u, i in USERS.items():
                        st.code(f"User: {u} | Pass: {i['password']}")
            
            return False
        return True
    
    def logout(self):
        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
    
    def get_user_info(self):
        if st.session_state.authenticated:
            return {'name': st.session_state.user_name, 'role': st.session_state.role}
        return None