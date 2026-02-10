import sys
from datetime import datetime, timedelta
from rich import print as rprint

from .data_manager import load_vocab, save_vocab, load_grammar, load_user_profile, save_user_profile
from .models import Vocabulary, GrammarLesson
from .quiz import QuizSession, GrammarQuizSession
from .gamification import add_xp, update_streak
from .ui import (
    display_dashboard, display_menu, display_grammar_list,
    display_lesson, display_question, get_user_answer,
    display_feedback, display_session_summary, clear_screen
)

def get_due_cards(vocab_list):
    now = datetime.now()
    due = []
    for card in vocab_list:
        if not card.last_review:
            due.append(card)
            continue
        last_date = datetime.strptime(card.last_review, '%Y-%m-%d')
        days_wait = 2 ** card.level
        if now > last_date + timedelta(days=days_wait):
            due.append(card)
    return due

def run_quiz(vocab_list, all_vocab, profile):
    session = QuizSession(vocab_list, all_vocab)
    while session.has_next():
        q = session.next_question()
        display_question(q, session.current_index, len(session.items))
        ans = get_user_answer(q)
        is_correct = session.check_answer(q, ans)

        display_feedback(is_correct, q.correct_answers[0], q.explanation)

        # Update SRS
        if isinstance(q.context, Vocabulary):
            if is_correct:
                q.context.level += 1
                q.context.last_review = datetime.now().strftime('%Y-%m-%d')
            else:
                q.context.level = max(0, q.context.level - 1)
                q.context.last_review = datetime.now().strftime('%Y-%m-%d')

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
        vocab = load_vocab()
        grammar = load_grammar()
        profile = load_user_profile()

        update_streak(profile)
        save_user_profile(profile)

        while True:
            mastered_count = sum(1 for v in vocab if v.level >= 5)
            display_dashboard(profile, mastered_count, len(profile.completed_lessons))
            choice = display_menu()

            if choice == "1":
                # Quiz Logic: due cards
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

            elif choice == "2":
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

            elif choice == "3":
                pass # Already on dashboard, just refreshes
            elif choice == "4":
                clear_screen()
                rprint("[bold green]See you next time! Ganbatte![/bold green]")
                break
    except KeyboardInterrupt:
        rprint("\n[bold red]Exiting...[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()
