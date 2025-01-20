import typer
from rich import print
from rich.prompt import Prompt, Confirm
import pandas as pd
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils import (
    initialize_bifrost,
    get_asset_id_and_xlsxform_path,
    update_asset_info,
)

app = typer.Typer()


def create_workbook_with_formatting(
    filepath: str, enable_formatting: bool, project_name: str
) -> None:
    """
    Creates an Excel workbook with pre-defined sheets and
    optionally applies conditional formatting.

    Args:
        filepath (str): The full path where the Excel workbook will be saved.
        enable_formatting (bool): Enable conditional formatting in workbook.
    """

    writer = pd.ExcelWriter(filepath, engine="xlsxwriter")

    survey_headers = [
        "type",
        "name",
        "label::English (en)",
        "hint::English (en)",
        "guidance_hint::English (en)",
        "required",
        "required_message::English (en)",
        "readonly",
        "relevant",
        "appearance",
        "default",
        "constraint",
        "constraint_message::English (en)",
        "calculation",
        "trigger",
        "choice_filter",
        "parameters",
        "repeat_count",
        "image::English (en)",
        "audio::English (en)",
        "video::English (en)",
        "note",
    ]
    choices_headers = [
        "list_name",
        "name",
        "label::English (en)",
        "image::English (en)",
    ]
    settings_headers = [
        "form_title",
        "form_id",
        "style",
        "version",
        "default_language",
        "allow_choice_duplicates",
        "instance_name",
    ]

    survey_df = pd.DataFrame(columns=survey_headers)
    choices_df = pd.DataFrame(columns=choices_headers)
    settings_df = pd.DataFrame(columns=settings_headers)
    settings_df.loc[len(settings_df)] = [project_name] + [""] * (
        len(settings_headers) - 1
    )

    survey_df.to_excel(writer, sheet_name="survey", index=False)
    choices_df.to_excel(writer, sheet_name="choices", index=False)
    settings_df.to_excel(writer, sheet_name="settings", index=False)

    workbook = writer.book
    survey_sheet = writer.sheets["survey"]

    if enable_formatting:

        formatting_styles = {
            "begin_group": workbook.add_format({"bg_color": "#b5e6a2"}),
            "begin_repeat": workbook.add_format({"bg_color": "#94dcf8"}),
            "end_group": workbook.add_format({"bg_color": "#f7c7ac"}),
            "end_repeat": workbook.add_format({"bg_color": "#e49edd"}),
        }

        num_columns = len(survey_headers)
        column_range = f"A2:{chr(64 + num_columns)}801"

        for condition, cell_format in formatting_styles.items():
            survey_sheet.conditional_format(
                column_range,
                {
                    "type": "formula",
                    "criteria": f'=$A2="{condition}"',
                    "format": cell_format,
                },
            )

    survey_sheet.autofit()
    writer.close()


@app.command("init")
def initialize_project():
    """
    Initializes a new project by creating a structured Excel workbook
    with optional conditional formatting.
    """

    def get_valid_project_name() -> str:
        while True:
            project_name = Prompt.ask("Enter the name of your project").strip()
            if project_name:
                return project_name
            print(
                "[red]Project name cannot be empty. "
                "Please enter a valid name.[/red]"
            )

    project_name = get_valid_project_name()
    default_dir = Path.cwd()
    project_dir = Prompt.ask(
        "Enter the directory path for the new project "
        "(leave blank to use the current directory)",
        default=str(default_dir),
    )

    project_dir_path = Path(project_dir).resolve()

    if not project_dir_path.exists():
        print(
            f"[yellow]The directory '{project_dir_path}' does not exist. "
            "Creating it...[/yellow]"
        )
        project_dir_path.mkdir(parents=True)

    if not project_dir_path.is_dir():
        print(
            f"[red]The specified path '{project_dir_path}' is not a directory.[/red]"
        )
        raise typer.Abort()

    project_file_name = f"{project_name}.xlsx"
    project_file_path = project_dir_path / project_file_name

    if project_file_path.exists():
        if not Confirm.ask(
            f"[red]The file '{project_file_path.name}' already exists. "
            "Overwrite it?[/red]"
        ):
            print(
                "[bold red]Aborting to avoid overwriting existing file.[/bold red]"
            )
            raise typer.Abort()

    enable_formatting = Confirm.ask(
        "Do you want to enable conditional formatting in the workbook?"
    )
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Fetching asset data...", start=False
        )

        progress.start_task(task)

        create_workbook_with_formatting(
            filepath=str(project_file_path),
            enable_formatting=enable_formatting,
            project_name=project_name,
        )
        progress.update(task, completed=100)

    print(
        f"[green]Project '{project_name}' has been successfully created at "
        f"'{project_file_path}'.[/green]"
    )
    update_asset_info(xlsx_path=project_file_path)


if __name__ == "__main__":
    app()
