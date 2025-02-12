import streamlit as st
from descope.descope_client import DescopeClient
from descope.exceptions import AuthException

DESCOPE_PROJECT_ID = str(st.secrets.get("DESCOPE_PROJECT_ID"))

descope_client = DescopeClient(project_id=DESCOPE_PROJECT_ID)


if "token" not in st.session_state:
    # User is not logged in
    if "code" in st.query_params:
        # Handle possible login
        code = st.query_params["code"]
        # Reset URL state
        st.query_params.clear()
        try:
            # Exchange code
            with st.spinner("Loading..."):
                jwt_response = descope_client.sso.exchange_token(code)
            st.session_state["token"] = jwt_response["sessionToken"].get("jwt")
            st.session_state["refresh_token"] = jwt_response["refreshSessionToken"].get(
                "jwt"
            )
            st.session_state["user"] = jwt_response["user"]
            st.rerun()
        except AuthException:
            st.error("Login failed!")
    st.warning("You're not logged in, pls login")
    with st.container(border=True):
        if st.button("Sign In with Google", use_container_width=True):
            oauth_response = descope_client.oauth.start(
                provider="google", return_url="https://excelmerged.streamlit.app/"
            )
            url = oauth_response["url"]
            # Redirect to Google
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={url}">',
                unsafe_allow_html=True,
            )
else:
    # User is logged in
    try:
        with st.spinner("Loading..."):
            jwt_response = descope_client.validate_and_refresh_session(
                st.session_state.token, st.session_state.refresh_token
            )
            # Persist refreshed token
            st.session_state["token"] = jwt_response["sessionToken"].get("jwt")
        st.title("Demo App")
        st.write("This is a demo app with Descope-powered authentication and SSO")
        st.subheader("Welcome! you're logged in")
        if "user" in st.session_state:
            user = st.session_state.user
            st.write("Name: " + user["name"])
        if st.button("Logout"):
            # Log out user
            del st.session_state.token
            st.rerun()
    except AuthException:
        # Log out user
        del st.session_state.token
        st.rerun()