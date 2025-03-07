from functools import wraps

# # Decorator to check if the user is authenticated.
# def with_auth(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
               
#         # session = workos.user_management.load_sealed_session(
#         #     sealed_session=request.cookies.get("wos_session"),
#         #     # cookie_password=cookie_password,
#         #     cookie_password=cookie_password,
#         # )
        
        
#         auth_response = session.authenticate()
#         if auth_response.authenticated:
#             return f(*args, **kwargs)

#         if (
#             auth_response.authenticated is False
#             and auth_response.reason == "no_session_cookie_provided"
#         ):
#             return make_response(redirect("/no-session-cookie-provided"))

#         # If no session, attempt a refresh
#         try:
#             result = session.refresh()
#             if result.authenticated is False:
#                 return make_response(redirect("/login"))

#             response = make_response(redirect(request.url))
#             response.set_cookie(
#                 "wos_session",
#                 result.sealed_session,
#                 # secure=True,
#                 # httponly=True,
#                 samesite="lax",
#             )
#             return response
#         except Exception as e:
#             response = make_response(redirect("/bad-refresh"))
#             response.delete_cookie("wos_session")
#             return response

#     return decorated_function