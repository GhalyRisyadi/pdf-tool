import shutil
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample.pdf"
    shutil.copy(fixtures_dir / "sample.pdf", dest)
    return dest


@pytest.fixture
def sample_with_images_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_with_images.pdf"
    shutil.copy(fixtures_dir / "sample_with_images.pdf", dest)
    return dest


@pytest.fixture
def sample_with_links_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_with_links.pdf"
    shutil.copy(fixtures_dir / "sample_with_links.pdf", dest)
    return dest


@pytest.fixture
def sample_with_tables_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_with_tables.pdf"
    shutil.copy(fixtures_dir / "sample_with_tables.pdf", dest)
    return dest


@pytest.fixture
def sample_encrypted_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_encrypted.pdf"
    shutil.copy(fixtures_dir / "sample_encrypted.pdf", dest)
    return dest


@pytest.fixture
def sample_restricted_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_restricted.pdf"
    shutil.copy(fixtures_dir / "sample_restricted.pdf", dest)
    return dest


@pytest.fixture
def sample_active_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_active.pdf"
    shutil.copy(fixtures_dir / "sample_active.pdf", dest)
    return dest


@pytest.fixture
def sample_pii_pdf(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample_pii.pdf"
    shutil.copy(fixtures_dir / "sample_pii.pdf", dest)
    return dest


@pytest.fixture
def sample_jpg(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample.jpg"
    shutil.copy(fixtures_dir / "sample.jpg", dest)
    return dest


@pytest.fixture
def sample_png(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample.png"
    shutil.copy(fixtures_dir / "sample.png", dest)
    return dest


@pytest.fixture
def sample_docx(fixtures_dir: Path, tmp_path: Path) -> Path:
    dest = tmp_path / "sample.docx"
    shutil.copy(fixtures_dir / "sample.docx", dest)
    return dest
