

from datetime import datetime, timedelta
from collections import defaultdict, deque
from src.domain.validators import validate_username, validate_password
from src.domain.errors import ValidationError
from src.domain.policies import can_change_password
from src.application.security.suspicious import record_failed_login, is_failed_login_suspicious, clear_failed_logins
from src.application.security.acl import CurrentUser

COOLDOWN_THRESHOLD = 5
COOLDOWN_MINUTES = 2

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

    if _is_in_cooldown(username):
        raise ValidationError("Please wait a moment before trying again")
    
    try:

        validate_username(username)

        username_norm = username
    except ValidationError:

        raise ValidationError("Invalid credentials")

    user = app.user_repo.get_by_username_norm(username_norm)
    if not user:
        raise ValidationError("Invalid credentials")

    if not app.password_hasher.verify(password, user['pw_hash']):

        record_failed_login(username_norm)

        app.logger.log('login_failed', username_norm, {'attempt': 'failed'}, False)

        if is_failed_login_suspicious(username_norm):
            app.logger.log('suspicious_activity', username_norm, {'reason': 'multiple_failed_logins'}, True)
            _set_cooldown(username_norm)
            raise ValidationError("Please wait a moment before trying again")
        
        raise ValidationError("Invalid credentials")

    clear_failed_logins(username_norm)
    app.logger.log('login_success', username_norm, {'user_id': user['id']}, False)
    
    return CurrentUser(
        id=user['id'],
        role=user['role'],
        username_norm=username_norm
    )

def change_password(app, current_user: CurrentUser, old_password: str, new_password: str):

    if not can_change_password(current_user.role):
        raise ValidationError("Super admin password cannot be changed")

    user = app.user_repo.get_by_username_norm(current_user.username_norm)
    if not user:
        raise ValidationError("User not found")

    if not app.password_hasher.verify(old_password, user['pw_hash']):
        raise ValidationError("Invalid current password")

    try:
        validated_new_password = validate_password(new_password)
    except ValidationError as e:
        raise ValidationError(f"New password invalid: {e}")

    new_hash = app.password_hasher.hash(validated_new_password)
    app.user_repo.update_password(current_user.id, new_hash)

    app.logger.log('password_changed', current_user.username_norm, {'user_id': current_user.id}, False)
