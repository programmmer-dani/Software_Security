# src/application/use_cases/auth.py

from datetime import datetime, timedelta
from collections import defaultdict, deque
from src.domain.validators import validate_username, validate_password
from src.domain.errors import ValidationError
from src.domain.policies import can_change_password
from src.application.security.suspicious import record_failed_login, is_failed_login_suspicious, clear_failed_logins
from src.application.security.acl import CurrentUser

# Cooldown thresholds
COOLDOWN_THRESHOLD = 5
COOLDOWN_MINUTES = 2

# Track cooldowns per user
_cooldowns = {}

def _is_in_cooldown(username: str) -> bool:
    if username in _cooldowns:
        cooldown_until = _cooldowns[username]
        if datetime.now() < cooldown_until:
            return True
        else:
            del _cooldowns[username]
    return False

def _set_cooldown(username: str):
    cooldown_until = datetime.now() + timedelta(minutes=COOLDOWN_MINUTES)
    _cooldowns[username] = cooldown_until

def login(app, username: str, password: str) -> CurrentUser:
    # Check cooldown first
    if _is_in_cooldown(username):
        raise ValidationError("Please wait a moment before trying again")
    
    try:
        # Validate username first
        validate_username(username)
        # Use validated username as-is for lookup
        username_norm = username
    except ValidationError:
        # Don't reveal if username format is wrong vs user doesn't exist
        raise ValidationError("Invalid credentials")
    
    # Get user from database
    user = app.user_repo.get_by_username_norm(username_norm)
    if not user:
        raise ValidationError("Invalid credentials")
    
    # Verify password
    if not app.password_hasher.verify(password, user['pw_hash']):
        # Record failed attempt
        record_failed_login(username_norm)
        
        # Log failed login
        app.logger.log('login_failed', username_norm, {'attempt': 'failed'}, False)
        
        # Check if suspicious
        if is_failed_login_suspicious(username_norm):
            app.logger.log('suspicious_activity', username_norm, {'reason': 'multiple_failed_logins'}, True)
            _set_cooldown(username_norm)
            raise ValidationError("Please wait a moment before trying again")
        
        raise ValidationError("Invalid credentials")
    
    # Success - clear failed attempts and log
    clear_failed_logins(username_norm)
    app.logger.log('login_success', username_norm, {'user_id': user['id']}, False)
    
    return CurrentUser(
        id=user['id'],
        role=user['role'],
        username_norm=username_norm
    )

def change_password(app, current_user: CurrentUser, old_password: str, new_password: str):
    # Check policy for password change permission
    if not can_change_password(current_user.role):
        raise ValidationError("Super admin password cannot be changed")
    
    # Get user to verify old password
    user = app.user_repo.get_by_username_norm(current_user.username_norm)
    if not user:
        raise ValidationError("User not found")
    
    # Verify old password
    if not app.password_hasher.verify(old_password, user['pw_hash']):
        raise ValidationError("Invalid current password")
    
    # Validate new password
    try:
        validated_new_password = validate_password(new_password)
    except ValidationError as e:
        raise ValidationError(f"New password invalid: {e}")
    
    # Hash new password and update
    new_hash = app.password_hasher.hash(validated_new_password)
    app.user_repo.update_password(current_user.id, new_hash)
    
    # Log password change
    app.logger.log('password_changed', current_user.username_norm, {'user_id': current_user.id}, False)
