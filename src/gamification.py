from .models import UserProfile
from datetime import datetime

XP_PER_LEVEL = 100

def add_xp(profile: UserProfile, amount: int):
    profile.xp += amount
    while profile.xp >= profile.level * XP_PER_LEVEL:
        profile.xp -= profile.level * XP_PER_LEVEL
        profile.level += 1
        print(f"🎉 LEVEL UP! You are now Level {profile.level}!")

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
