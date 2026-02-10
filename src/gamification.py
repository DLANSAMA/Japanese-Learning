from .models import UserProfile
from datetime import datetime

XP_PER_LEVEL = 100

def add_xp(profile: UserProfile, amount: int):
    profile.xp += amount
    while profile.xp >= profile.level * XP_PER_LEVEL:
        profile.xp -= profile.level * XP_PER_LEVEL
        profile.level += 1
        # In headless mode this print might break JSON output if not handled carefully,
        # but typical headless runs capture stdout separately or just ignore this if mixed.
        # For pure JSON headless, we should probably suppress this print or use logging.
        # Since headless.py handles output manually, this print goes to stderr or is just text.
        # Ideally, return events instead of printing.
        pass

def update_streak(profile: UserProfile):
    today = datetime.now().strftime('%Y-%m-%d')
    if profile.last_login == today:
        return

    if not profile.last_login:
        profile.streak = 1
    else:
        last_date = datetime.strptime(profile.last_login, '%Y-%m-%d')
        days_diff = (datetime.now() - last_date).days
        if days_diff == 1:
            profile.streak += 1
        else:
            profile.streak = 1

    profile.last_login = today
