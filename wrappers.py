from functools import wraps
from flask import session, redirect, url_for, request, flash


#login decorator
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if ('user_id' in session):
            return f(*args, **kwargs)

        session.clear()        
        flash("Please login to access the site.", "error")
        
        return redirect(url_for("main_page_module.login"))
    
    return wrapper

def online_required(online):  # extra_arg is your new parameter
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if ('user_id' in session):
                return f(*args, **kwargs)
            elif online == "1":
                return f(*args, **kwargs)
            session.clear()
            
            return redirect(url_for("main_page_module.offline"))
        
        return wrapper
    return decorator