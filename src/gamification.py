from .models import UserProfile
from datetime import datetime

XP_PER_LEVEL = 100

def add_xp(profile: UserProfile, amount: int):
    profile.xp += amount
    while profile.xp >= profile.level * XP_PER_LEVEL:
        profile.xp -= profile.level * XP_PER_LEVEL
        profile.level += 1
        # Avoid print in headless mode if possible, but for now we keep it or rely on UI layer to display events
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

def calculate_rewards(is_correct: bool, current_streak: int) -> tuple[int, int]:
    """
    Calculates XP and Gems based on correctness and streak.
    Returns (xp, gems)
    """
    if not is_correct:
        return 0, 0

    xp = 10 + (current_streak * 1) # Bonus XP for streak
    xp = min(xp, 50) # Cap XP per answer

    gems = 1 # Flat rate for now

    return xp, gems
