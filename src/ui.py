import time

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .models import GrammarLesson, UserProfile, Vocabulary

console = Console()

THEMES = {
    "default": {"border": "blue", "title": "bold green", "highlight": "yellow"},
    "cyberpunk": {"border": "magenta", "title": "bold cyan", "highlight": "bright_green"},
    "zen": {"border": "white", "title": "italic white", "highlight": "dim cyan"}
}

MASCOT = r"""
 /\_/\
( o.o )
 > ^ <
"""

def get_theme(theme_name: str):
    return THEMES.get(theme_name, THEMES["default"])

def clear_screen():
    console.clear()

def display_dashboard(profile: UserProfile, vocab_count: int, grammar_count: int):
    clear_screen()
    theme = get_theme(profile.settings.theme)

    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)

    grid.add_row(
        Panel(f"[{theme['highlight']}]{profile.level}[/{theme['highlight']}]", title="Level", border_style=theme['border']),
        Panel(f"[{theme['highlight']}]{profile.xp}[/{theme['highlight']}]", title="XP", border_style=theme['border']),
        Panel(f"[{theme['highlight']}]{profile.streak} Days[/{theme['highlight']}]", title="Streak", border_style=theme['border'])
    )

    header_content = f"[{theme['title']}]Welcome back, Learner![/{theme['title']}]\n\nCards Mastered: {vocab_count}\nGrammar Lessons: {grammar_count}\n\n[dim]Track: {profile.selected_track}[/dim]"

    # Add Mascot
    mascot_panel = Panel(Align.center(MASCOT), border_style=theme['border'], width=20)
    info_panel = Panel(Align.center(header_content), title="🇯🇵 Japanese Learning Hub", subtitle="Keep going!", border_style=theme['border'])

    # Layout header with mascot
    header_grid = Table.grid(expand=True)
    header_grid.add_column(ratio=1)
    header_grid.add_column(ratio=3)
    header_grid.add_row(mascot_panel, info_panel)

    console.print(header_grid)
    console.print(grid)
    console.print("\n")

def display_menu() -> str:
    table = Table(title="Main Menu", show_header=False, box=None)
    table.add_row("[1] 👨‍🏫 Start Lesson (Study Mode)")
    table.add_row("[2] 📝 Quiz (Review Due Cards)")
    table.add_row("[3] 📖 Learn Grammar")
    table.add_row("[4] ⚙️ Settings (Track/Theme)")
    table.add_row("[5] ❌ Exit")

    console.print(table)
    return Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="2")

def display_settings_menu(profile: UserProfile):
    clear_screen()
    console.print(Panel("[bold]Settings[/bold]", border_style="blue"))

    console.print(f"Current Track: [green]{profile.selected_track}[/green]")
    console.print(f"Current Theme: [cyan]{profile.settings.theme}[/cyan]")
    console.print("\n[1] Change Track")
    console.print("[2] Change Theme")
    console.print("[3] Back")

    choice = Prompt.ask("Select option", choices=["1", "2", "3"])

    if choice == "1":
        console.print("\nAvailable Tracks:")
        tracks = ["General", "Pop Culture", "Business", "Travel"]
        for i, t in enumerate(tracks):
            console.print(f"[{i+1}] {t}")
        sel = Prompt.ask("Select Track", choices=[str(i+1) for i in range(len(tracks))])
        profile.selected_track = tracks[int(sel)-1]
        console.print(f"Track updated to {profile.selected_track}!")
        time.sleep(1)

    elif choice == "2":
        console.print("\nAvailable Themes:")
        themes = list(THEMES.keys())
        for i, t in enumerate(themes):
            console.print(f"[{i+1}] {t}")
        sel = Prompt.ask("Select Theme", choices=[str(i+1) for i in range(len(themes))])
        profile.settings.theme = themes[int(sel)-1]
        console.print(f"Theme updated to {profile.settings.theme}!")
        time.sleep(1)

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
