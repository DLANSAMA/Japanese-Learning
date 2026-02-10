import sys
from datetime import datetime, timedelta
from rich import print as rprint

from .data_manager import load_vocab, save_vocab, load_grammar, load_user_profile, save_user_profile
from .models import Vocabulary, GrammarLesson
from .quiz import QuizSession, GrammarQuizSession
from .gamification import add_xp, update_streak
from .srs_engine import update_card_srs
from .ui import (
    display_dashboard, display_menu, display_grammar_list,
    display_lesson, display_question, get_user_answer,
    display_feedback, display_session_summary, clear_screen,
    display_study_session
)
from .study import get_new_items, mark_as_learning
from .migrate_data import migrate

def get_due_cards(vocab_list):
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    due = []

    # Sort vocab by due date to prioritize overdue items
    sorted_vocab = sorted(vocab_list, key=lambda v: v.due_date if v.due_date else "0000-00-00")

    for card in sorted_vocab:
        # Exclude 'new' items
        if card.status == 'new':
            continue

        if not card.due_date:
            # If no due date but status is learning/mastered
            due.append(card)
        elif card.due_date <= today_str:
            due.append(card)

    return due

def run_study_mode(vocab, profile):
    # Get 5 new items
    new_items = [v for v in vocab if v.status == 'new'][:5]
    if not new_items:
        rprint("[bold green]🎉 No new items to learn! You've seen everything![/bold green]")
        import time
        time.sleep(2)
        return

    # Display loop
    display_study_session(new_items)

    # Mark all as learning
    for item in new_items:
        mark_as_learning(item)

    save_vocab(vocab)
    rprint("[bold green]Lesson Complete! Items added to your review queue.[/bold green]")
    input("Press Enter to continue...")

def run_quiz(vocab_list, all_vocab, profile):
    session = QuizSession(vocab_list, all_vocab, settings=profile.settings)
    while session.has_next():
        q = session.next_question()
        display_question(q, session.current_index, len(session.items))
        ans = get_user_answer(q)
        is_correct = session.check_answer(q, ans)

        display_feedback(is_correct, q.correct_answers[0], q.explanation)

        # Update SRS
        if isinstance(q.context, Vocabulary):
            # Map correctness to rating:
            # Correct -> 5 (Easy) for now
            # Incorrect -> 0 (Fail)
            rating = 5 if is_correct else 0
            update_card_srs(q.context, rating)
            if q.context.level >= 5 and q.context.interval > 21:
                q.context.status = 'mastered'

    xp_gained = session.score * 10
    add_xp(profile, xp_gained)
    display_session_summary(session.score, session.total, xp_gained)

def run_grammar_lesson(lesson, profile):
    display_lesson(lesson)
    session = GrammarQuizSession(lesson)
    while session.has_next():
        q = session.next_question()
        display_question(q, session.current_index, len(session.exercises))
        ans = get_user_answer(q)
        is_correct = session.check_answer(q, ans)
        display_feedback(is_correct, q.correct_answers[0], q.explanation)

    xp_gained = session.score * 15 # More XP for grammar
    add_xp(profile, xp_gained)
    if session.score == session.total:
        if lesson.id not in profile.completed_lessons:
             profile.completed_lessons.append(lesson.id)
    display_session_summary(session.score, session.total, xp_gained)

def main():
    try:
        # Auto-migrate data if needed
        # We call the migrate function directly. It checks and runs if needed.
        # This ensures users don't start with "new" status for learned cards.
        # Ideally this should be silent or minimal output unless migration happens.
        # But migrate() prints. Let's assume that's fine for CLI startup.
        try:
             migrate()
        except Exception as e:
             rprint(f"[red]Migration failed: {e}[/red]")

        vocab = load_vocab()
        grammar = load_grammar()
        profile = load_user_profile()

        update_streak(profile)
        save_user_profile(profile)

        while True:
            # Mastered count based on status
            mastered_count = sum(1 for v in vocab if v.status == 'mastered')
            display_dashboard(profile, mastered_count, len(profile.completed_lessons))
            choice = display_menu()

            if choice == "1":
                # Start Lesson (Study Mode)
                run_study_mode(vocab, profile)

            elif choice == "2":
                # Quiz Logic: due cards (Review)
                due = get_due_cards(vocab)
                if not due:
                    rprint("[bold green]🎉 No cards due for review! Great job![/bold green]")
                    import time
                    time.sleep(2)
                    continue

                # Limit to 10 for bite-sized sessions
                session_cards = due[:10]
                run_quiz(session_cards, vocab, profile)
                save_user_profile(profile)
                save_vocab(vocab)

            elif choice == "3":
                lid = display_grammar_list(grammar)
                if lid == "back": continue
                # Find lesson
                lesson = next((l for l in grammar if l.id == lid), None)
                if lesson:
                    run_grammar_lesson(lesson, profile)
                    save_user_profile(profile)
                else:
                    rprint("[red]Lesson not found![/red]")
                    import time
                    time.sleep(1)

            elif choice == "4":
                # Stats view logic could go here or separate function
                # For now just refresh dashboard
                pass

            elif choice == "5":
                clear_screen()
                rprint("[bold green]See you next time! Ganbatte![/bold green]")
                break
    except KeyboardInterrupt:
        rprint("\n[bold red]Exiting...[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()
