from pathlib import Path
from typing import Final

VAK_LIST_URL: Final[str] = "https://phdru.com/mydocs/pervak17072023.pdf"
VAK_JOURNALS_PDF: Path = Path("data") / "pdfs" / VAK_LIST_URL.split("/")[-1]
