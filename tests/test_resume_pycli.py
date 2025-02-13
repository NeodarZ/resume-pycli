from typer.testing import CliRunner
import json
from pathlib import Path
from shutil import copytree
from importlib import metadata

import resume_pycli
from resume_pycli.cli import app

import unittest
from unittest.mock import patch


class ResumeCliTestCase(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

        if hasattr(resume_pycli.cli.Options, "resume"):
            del resume_pycli.cli.Options.resume
        if hasattr(resume_pycli.cli.Options, "theme"):
            del resume_pycli.cli.Options.theme

    def test_version(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["version"])
            assert result.stdout.strip() == metadata.version("resume_pycli")
            assert result.exit_code == 0

    def test_validate(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["validate"])
            assert result.exit_code == 0

    def test_validate_no_resume(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(app, ["validate"])
            assert result.exit_code == 1

    def test_validate_bad_key(self):
        with self.runner.isolated_filesystem():
            Path("resume.json").write_text('{"bad_key": "random value"}')
            result = self.runner.invoke(app, ["validate"])
            assert result.exit_code != 0

    def test_export(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["export"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert Path("public", "index.pdf").exists()

    def test_export_no_html(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["export", "--no-html"])
            assert result.exit_code == 0
            assert Path("public", "index.pdf").exists()
            assert not Path("public", "index.html").exists()

    def test_export_only_pdf(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["export", "--pdf"])
            assert result.exit_code == 0
            assert Path("public", "index.pdf").exists()
            assert not Path("public", "index.html").exists()

    def test_export_no_pdf(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["export", "--no-pdf"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert not Path("public", "index.pdf").exists()

    def test_export_only_html(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["export", "--html"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert not Path("public", "index.pdf").exists()

    def test_export_custom_theme(self):
        with self.runner.isolated_filesystem():
            lib_dir = Path(resume_pycli.__file__).parent
            resume = lib_dir.joinpath("resume.json").read_text()
            copytree(
                lib_dir.joinpath("themes", "base"),
                Path.cwd().joinpath("themes", "custom"),
                dirs_exist_ok=True,
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["--theme", "custom", "export"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert Path("public", "index.pdf").exists()

    def test_export_with_image(self):
        with self.runner.isolated_filesystem():
            lib_dir = Path(resume_pycli.__file__).parent
            # create a dummy image and inject it into resume.json
            image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            with open("image.jpg", "wb") as image_file:
                image_file.write(image.encode())
            resume = json.loads(lib_dir.joinpath("resume.json").read_text())
            resume["basics"]["image"] = "image.jpg"
            Path("resume.json").write_text(json.dumps(resume))
            result = self.runner.invoke(app, ["export"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert Path("public", "index.pdf").exists()

    def test_export_stackoverflow_theme(self):
        with self.runner.isolated_filesystem():
            lib_dir = Path(resume_pycli.__file__).parent
            resume = lib_dir.joinpath("resume.json").read_text()
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(app, ["--theme", "stackoverflow", "export"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert Path("public", "index.pdf").exists()
            assert Path("public", "static").is_dir()

    def test_export_stackoverflow_theme_with_image(self):
        with self.runner.isolated_filesystem():
            lib_dir = Path(resume_pycli.__file__).parent
            # create a dummy image and inject it into resume.json
            image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            with open("image.jpg", "wb") as image_file:
                image_file.write(image.encode())
            resume = json.loads(lib_dir.joinpath("resume.json").read_text())
            resume["basics"]["image"] = "image.jpg"
            Path("resume.json").write_text(json.dumps(resume))
            result = self.runner.invoke(app, ["--theme", "stackoverflow", "export"])
            assert result.exit_code == 0
            assert Path("public", "index.html").exists()
            assert Path("public", "index.pdf").exists()
            assert Path("public", "static").is_dir()

    def test_export_pdf_backend_playwright(self):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(
                app, ["export", "--no-html", "--pdf-backend", "playwright"]
            )
            assert result.exit_code == 0
            assert Path("public", "index.pdf").exists()

    def fake_pdf(*args, **kwargs):
        Path("public/index.pdf").write_bytes(b"")

    @patch("resume_pycli.pdf.export_weasyprint", wraps=fake_pdf)
    def test_export_pdf_backend_weasyprint(self, mocker):
        with self.runner.isolated_filesystem():
            resume = (
                Path(resume_pycli.__file__).parent.joinpath("resume.json").read_text()
            )
            Path("resume.json").write_text(resume)
            result = self.runner.invoke(
                app, ["export", "--no-html", "--pdf-backend", "weasyprint"]
            )
            assert result.exit_code == 0
            assert Path("public", "index.pdf").exists()
