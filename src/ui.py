from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown
from rich.layout import Layout
from rich.align import Align
from rich import print as rprint
import time

from .models import UserProfile, Vocabulary, GrammarLesson

console = Console()

def clear_screen():
    console.clear()

def display_dashboard(profile: UserProfile, vocab_count: int, grammar_count: int):
    clear_screen()

    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)

    grid.add_row(
        Panel(f"[bold cyan]{profile.level}[/bold cyan]", title="Level", border_style="cyan"),
        Panel(f"[bold yellow]{profile.xp}[/bold yellow]", title="XP", border_style="yellow"),
        Panel(f"[bold red]{profile.streak} Days[/bold red]", title="Streak", border_style="red")
    )

    console.print(Panel(
        Align.center(f"[bold green]Welcome back, Learner![/bold green]\n\nCards Mastered: {vocab_count}\nGrammar Lessons: {grammar_count}"),
        title="🇯🇵 Japanese Learning Hub",
        subtitle="Keep going!"
    ))
    console.print(grid)
    console.print("\n")

def display_menu() -> str:
    table = Table(title="Main Menu", show_header=False, box=None)
    table.add_row("[1] 👨‍🏫 Start Lesson (Study Mode)")
    table.add_row("[2] 📝 Quiz (Review Due Cards)")
    table.add_row("[3] 📖 Learn Grammar")
    table.add_row("[4] 📊 View Stats")
    table.add_row("[5] ❌ Exit")

    console.print(table)
    return Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="2")

def display_grammar_list(lessons: list[GrammarLesson]) -> str:
    clear_screen()
    table = Table(title="Grammar Lessons")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Description")

    for lesson in lessons:
        table.add_row(lesson.id, lesson.title, lesson.description)

    console.print(table)
    return Prompt.ask("Enter Lesson ID to start (or 'back')", default="back")

def display_lesson(lesson: GrammarLesson):
    clear_screen()
    console.print(Panel(f"[bold magenta]{lesson.title}[/bold magenta]", title="Grammar Lesson"))
    console.print(Markdown(f"## {lesson.description}"))
    console.print(Markdown(lesson.explanation))

    console.print(Panel(f"[bold]Structure:[/bold] {lesson.structure}", border_style="blue"))

    table = Table(title="Examples", show_header=True)
    table.add_column("Japanese")
    table.add_column("Romaji")
    table.add_column("English")

    for ex in lesson.examples:
        table.add_row(ex.jp, ex.romaji, ex.en)

    console.print(table)

    Prompt.ask("\nPress Enter to start practice exercises...")

def display_question(question_obj, current: int, total: int):
    clear_screen()
    progress = f"Question {current}/{total}"

    content = f"[bold]{question_obj.question_text}[/bold]"

    if question_obj.type == "multiple_choice":
        content += "\n\n"
        for i, opt in enumerate(question_obj.options):
            content += f"{i+1}. {opt}\n"

    console.print(Panel(content, title=f"Quiz - {progress}", border_style="green"))

def get_user_answer(question_obj) -> str:
    if question_obj.type == "multiple_choice":
        choices = [str(i+1) for i in range(len(question_obj.options))]
        selection = Prompt.ask("Choose correct option", choices=choices)
        return question_obj.options[int(selection)-1]
    else:
        return Prompt.ask("Your Answer")

def display_feedback(is_correct: bool, correct_answer: str, explanation: str = None):
    if is_correct:
        console.print("[bold green]✅ Correct![/bold green]")
    else:
        console.print(f"[bold red]❌ Incorrect![/bold red] The answer was: [bold]{correct_answer}[/bold]")

    if explanation:
        console.print(f"[dim]{explanation}[/dim]")

    time.sleep(1.5)

def display_session_summary(score: int, total: int, xp_gained: int):
    clear_screen()
    console.print(Panel(
        Align.center(f"[bold]Session Complete![/bold]\n\nScore: {score}/{total}\nXP Gained: +{xp_gained}"),
        title="Summary",
        border_style="gold1"
    ))
    Prompt.ask("Press Enter to continue...")

def display_study_session(items: list[Vocabulary]):
    clear_screen()
    console.print(Panel(f"[bold]Study Mode[/bold]\nLearning {len(items)} new words...", border_style="magenta"))
    time.sleep(1)

    for item in items:
        clear_screen()
        content = f"""
        [bold cyan]{item.word}[/bold cyan] ({item.kana})
        [italic]{item.romaji}[/italic]

        [bold white]{item.meaning}[/bold white]

        Tags: {', '.join(item.tags)}
        """
        console.print(Panel(Align.center(content), title="New Vocabulary", border_style="blue"))
        Prompt.ask("Press Enter when you've memorized this...")
