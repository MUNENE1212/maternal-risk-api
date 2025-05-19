# app/routers/auth_router.py
from fastapi import APIRouter, HTTPException, Request, Form, Depends, Response, status
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from datetime import datetime, timedelta
import logging
import re
import json

from app.db.database import users_collection
from app.models.user_model import UserCreate
from app.auth.auth_utils import (
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM
)

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger("auth")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def normalize_phone(phone: str) -> str:
    """Normalize phone numbers to +254 format consistently"""
    # First strip all non-digits
    cleaned = re.sub(r'\D', '', phone)
    
    # Log original and cleaned phone for debugging
    logger.debug(f"Original phone: {phone}, Cleaned: {cleaned}")
    
    # Handle different formats
    if cleaned.startswith('0'):
        return f'+254{cleaned[1:]}'
    elif cleaned.startswith('254'):
        return f'+{cleaned}'
    elif re.match(r'^7\d{8}$', cleaned):  # Starts with 7 followed by 8 digits
        return f'+254{cleaned}'
    else:
        # For any other format, ensure it has a + prefix
        return f'+{cleaned}' if not cleaned.startswith('+') else cleaned


def validate_phone_format(phone: str) -> bool:
    """Validate that phone is in the correct +254XXXXXXXXX format"""
    return bool(re.fullmatch(r'^\+254\d{9}$', phone))


@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("app/static/assets/favicon.ico")


def show_login_error(request: Request, error: str):
    try:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": error,
            "news_posts": [
                {"title": "Health Tip", "snippet": "Stay hydrated during pregnancy - aim for 8-10 glasses of water daily."},
                {"title": "System Alert", "snippet": "If login issues persist, please contact support."}
            ]
        })
    except Exception as e:
        logger.error(f"Error template rendering failed: {str(e)}")
        return HTMLResponse("<h1>Authentication Service Error</h1>", status_code=500)


# auth_router.py
def get_dashboard_url_by_role(role: str) -> str:
    """All roles use the same dashboard endpoint"""
    return "/dashboard"


@router.post("/login", response_class=HTMLResponse)
async def login_user_form(
    request: Request,
    phone_number: str = Form(...),
    password: str = Form(...),
    response: Response = None
):
    try:
        # Check if request is AJAX
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        
        # Log the original phone_number for debugging
        logger.info(f"Original login phone: {phone_number}")
        
        # Normalize and validate phone number
        phone = normalize_phone(phone_number)
        logger.info(f"Login attempt for normalized phone: {phone}")
        
        if not validate_phone_format(phone):
            logger.warning(f"Invalid phone format: {phone}")
            error_msg = "Invalid phone number format. Please use a valid Kenyan number."
            if is_ajax:
                return JSONResponse({"success": False, "message": error_msg}, status_code=400)
            return show_login_error(request, error_msg)

        # Find user by phone
        user = await users_collection.find_one({"phone_number": phone})
        
        # Debug log if user not found
        if not user:
            logger.warning(f"User not found: {phone}")
            # Try finding with alternative formats for debugging
            alternative_formats = [
                phone.replace('+', ''),
                phone[1:] if phone.startswith('+') else phone,
                phone[4:] if phone.startswith('+254') else phone
            ]
            logger.debug(f"Trying alternative formats: {alternative_formats}")
            for alt_format in alternative_formats:
                debug_user = await users_collection.find_one({"phone_number": alt_format})
                if debug_user:
                    logger.debug(f"Found user with alternative format: {alt_format}")
            
            error_msg = "Account not found. Please check your phone number."
            if is_ajax:
                return JSONResponse({"success": False, "message": error_msg}, status_code=400)
            return show_login_error(request, error_msg)

        # Check password
        logger.debug(f"Verifying password for user: {phone}")
        if not bcrypt.verify(password, user["password"]):
            logger.warning(f"Password mismatch for {phone}")
            
            # Handle failed login attempts
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$inc": {"failed_login_attempts": 1}}
            )
            
            error_msg = "Incorrect password. Please try again."
            if is_ajax:
                return JSONResponse({"success": False, "message": error_msg}, status_code=400)
            return show_login_error(request, error_msg)

        # Reset failed login attempts on successful login
        await users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "last_login": datetime.utcnow()
                }
            }
        )

        # Get role-specific dashboard URL
        user_role = user.get("role", "patient")
        dashboard_url = get_dashboard_url_by_role(user_role)
        logger.info(f"User {phone} with role {user_role} redirecting to {dashboard_url}")

        # Create token
        token_data = {
            "sub": user["phone_number"],
            "role": user_role,
            "id": str(user["_id"]),
            "name": user["full_name"]
        }
        token = create_access_token(token_data)
        logger.info(f"Successful login for: {phone} with role: {user_role}")

        # Handle response based on request type
        if is_ajax:
            # For AJAX requests, return JSON with role-specific redirect
            return JSONResponse({
                "success": True,
                "redirect": dashboard_url,
                "role": user_role
            })
        else:
            # For form submissions, redirect with cookie to role-specific dashboard
            response = RedirectResponse(url=dashboard_url, status_code=302)
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=False,  # Set to False for HTTP testing environments
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,  # 7 day
                path='/'
            )
            return response

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        error_msg = "An error occurred during login. Please try again."
        
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JSONResponse({"success": False, "message": error_msg}, status_code=500)
        return show_login_error(request, error_msg)

@router.post("/signup")
async def signup_user_form(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    role: str = Form("patient")
):
    try:
        # Check if request is AJAX
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        
        # Validate input data
        validation_errors = []
        
        if len(first_name.strip()) < 2:
            validation_errors.append("First name must be at least 2 characters")
        
        if len(last_name.strip()) < 2:
            validation_errors.append("Last name must be at least 2 characters")
        
        if len(password) < 8:
            validation_errors.append("Password must be at least 8 characters")
        
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            validation_errors.append("Password must contain both letters and numbers")

        # Log the original phone number for debugging
        logger.info(f"Original signup phone: {phone_number}")
        
        # Normalize and validate phone
        try:
            normalized_phone = normalize_phone(phone_number)
            logger.info(f"Normalized signup phone: {normalized_phone}")
            
            if not validate_phone_format(normalized_phone):
                validation_errors.append("Please enter a valid Kenyan phone number")
        except Exception as e:
            logger.error(f"Phone normalization error: {str(e)}")
            validation_errors.append("Invalid phone number format")
            normalized_phone = ""
            
        # If validation errors, return them
        if validation_errors:
            error_msg = validation_errors[0]  # Return first error
            if is_ajax:
                return HTMLResponse(
                    content=f"<div class='text-red-600'>{error_msg}</div>",
                    status_code=400
                )
            return show_signup_error(request, error_msg)
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"phone_number": normalized_phone})
        if existing_user:
            error_msg = "This phone number is already registered"
            if is_ajax:
                return HTMLResponse(
                    content=f"<div class='text-red-600'>{error_msg}</div>",
                    status_code=400
                )
            return show_signup_error(request, error_msg)

        # Create new user
        user_data = {
            "full_name": f"{first_name.strip()} {last_name.strip()}",
            "phone_number": normalized_phone,
            "password": bcrypt.hash(password),
            "role": role.lower(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "failed_login_attempts": 0
        }

        logger.info(f"Creating new user with phone: {normalized_phone}, role: {role.lower()}")
        result = await users_collection.insert_one(user_data)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create user")

        logger.info(f"New user created: {result.inserted_id}")

        # Return appropriate response based on request type
        if is_ajax:
            return HTMLResponse(
                content="<div class='text-green-600'>✅ Registration successful! You can now login</div>"
            )
        
        return RedirectResponse(url="/auth/login?success=1", status_code=302)

    except Exception as e:
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        error_msg = "Registration failed. Please try again."
        
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HTMLResponse(
                content=f"<div class='text-red-600'>{error_msg}</div>",
                status_code=400
            )
            
        return show_signup_error(request, error_msg)

def show_signup_error(request: Request, error: str):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "signup_error": error,
        "news_posts": [
            {"title": "Registration Help", "snippet": "Make sure your phone number is in the format 7XXXXXXXX"},
            {"title": "Password Tips", "snippet": "Use a combination of letters, numbers and symbols for security"}
        ]
    })

@router.get("/logout")
async def logout():
    try:
        response = RedirectResponse(url="/auth/login?logged_out=1", status_code=302)
        response.delete_cookie("access_token")
        logger.info("User logged out successfully")
        return response
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)
        
@router.get("/login", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None,
        "news_posts": [
            {"title": "Welcome to MamaGuardian", "snippet": "Track your pregnancy journey with ease"},
            {"title": "Prenatal Care", "snippet": "Regular checkups are essential for a healthy pregnancy"},
            {"title": "Nutrition Tips", "snippet": "Eat a balanced diet rich in folate and iron"}
        ]
    })

@router.get("/test-auth")
async def test_auth(current_user = Depends(get_current_user)):
    return JSONResponse({
        "status": "authenticated",
        "user": current_user["phone_number"],
        "role": current_user["role"],
        "dashboard": get_dashboard_url_by_role(current_user["role"])
    })
