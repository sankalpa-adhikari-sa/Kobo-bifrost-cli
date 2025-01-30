import os

import pandas as pd

from bifrost_cli.commands.initialize import app as init_app


def test_initialize_project_default_path(
    runner, isolated_filesystem, project_name, expected_headers
):
    """Test successful project creation with default options"""

    result = runner.invoke(
        init_app,
        input=f"{project_name}\n\ny\n",
    )

    assert result.exit_code == 0
    assert f"Project '{project_name}' has been successfully created" in result.stdout

    file_path = os.path.join(isolated_filesystem, f"{project_name}.xlsx")
    assert os.path.exists(f"{project_name}.xlsx")

    workbook = pd.ExcelFile(f"{project_name}.xlsx")
    assert set(workbook.sheet_names) == {"survey", "choices", "settings"}
    for sheet_name, expected_sheet_headers in expected_headers.items():
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        assert list(df.columns) == expected_sheet_headers


def test_initialize_project_empty_filename(
    runner, isolated_filesystem, project_name, expected_headers
):
    """Test successful project creation with default options"""

    result = runner.invoke(
        init_app,
        input=f"\n{project_name}\n\ny\n",
    )

    assert result.exit_code == 0
    assert (
        "Project name cannot be empty or contain '='. Please enter a valid name."
        in result.stdout
    )
    assert f"Project '{project_name}' has been successfully created" in result.stdout

    file_path = os.path.join(isolated_filesystem, f"{project_name}.xlsx")
    assert os.path.exists(f"{project_name}.xlsx")

    workbook = pd.ExcelFile(f"{project_name}.xlsx")
    assert set(workbook.sheet_names) == {"survey", "choices", "settings"}
    for sheet_name, expected_sheet_headers in expected_headers.items():
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        assert list(df.columns) == expected_sheet_headers


def test_initialize_project_custom_file_path(
    runner, isolated_filesystem, project_name, expected_headers
):
    """Test successful project creation with default options"""

    result = runner.invoke(
        init_app,
        input=f"{project_name}\n{isolated_filesystem}\ny\n",
    )

    assert result.exit_code == 0
    assert f"Project '{project_name}' has been successfully created" in result.stdout

    file_path = os.path.join(isolated_filesystem, f"{project_name}.xlsx")
    assert os.path.exists(f"{project_name}.xlsx")

    workbook = pd.ExcelFile(f"{project_name}.xlsx")
    assert set(workbook.sheet_names) == {"survey", "choices", "settings"}
    for sheet_name, expected_sheet_headers in expected_headers.items():
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        assert list(df.columns) == expected_sheet_headers


def test_initialize_project_custom_file_path_overwrite(
    runner, isolated_filesystem, project_name, expected_headers
):
    """Test successful project creation with default options"""
    file_path = os.path.join(isolated_filesystem, f"{project_name}.xlsx")
    os.makedirs(isolated_filesystem, exist_ok=True)
    with open(file_path, "w") as f:
        f.write("dummy content")

    result = runner.invoke(
        init_app,
        input=f"{project_name}\n{isolated_filesystem}\ny\ny\n",
    )

    assert result.exit_code == 0
    assert (
        f"The file '{project_name}.xlsx' already exists. Overwrite it?" in result.stdout
    )
    assert f"Project '{project_name}' has been successfully created" in result.stdout

    assert os.path.exists(f"{project_name}.xlsx")

    workbook = pd.ExcelFile(f"{project_name}.xlsx")
    assert set(workbook.sheet_names) == {"survey", "choices", "settings"}
    for sheet_name, expected_sheet_headers in expected_headers.items():
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        assert list(df.columns) == expected_sheet_headers
