from multiprocessing import get_context
from pathlib import Path
from typing import Final

import camelot
import httpx
import numpy as np
import pandas as pd

VAK_LIST_URL: Final[str] = "https://phdru.com/mydocs/pervak17072023.pdf"
PAGE_COUNT = 12
PROCESSES_NUM = 4
COLUMNS_NAMES: Final[list[str]] = ["id", "name", "issn", "specialties", "included_date"]


def read_pdf_table(pdf_path: str, pages: str):
    return camelot.read_pdf(pdf_path, pages=pages)


def parse_vak():
    # response: httpx.Response = httpx.get(VAK_LIST_URL)
    pdf: Path = Path("data") / "pdfs" / VAK_LIST_URL.split("/")[-1]

    # with pdf.open("bw") as pdf_file:
    #     pdf_file.write(response.content)

    page_per_process = PAGE_COUNT // PROCESSES_NUM
    pages = [f"{i + 1}-{i+page_per_process}" for i in range(0, PAGE_COUNT + 1, page_per_process)]
    pages.append(f"{PROCESSES_NUM * page_per_process + 1}-12")

    tables = []
    with get_context('spawn').Pool(PROCESSES_NUM) as pool:
        for _tables in pool.starmap(read_pdf_table, ((str(pdf), _pages) for _pages in pages)):
            tables.extend(_tables)

    # tables = camelot.read_pdf(str(pdf), pages='1,2')

    vak_list: pd.DataFrame = pd.DataFrame(columns=COLUMNS_NAMES)
    # concat pages
    for table in tables:
        table.df.columns = COLUMNS_NAMES
        vak_list = pd.concat([vak_list, table.df], ignore_index=True)
    vak_list.reset_index(inplace=True)

    # drop first row because of this is a header
    vak_list = vak_list.loc[1:]
    # fill empty string as NaN
    vak_list.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    # split dates
    splitted_dates = vak_list["included_date"].str.extract(
        r'.*(?P<from_date>\d{2}+\.\d{2}\.\d{4})([\S\W]*(?P<to_date>\d{2}+\.\d{2}\.\d{4}))?')
    splitted_dates["from_date"] = pd.to_datetime(splitted_dates["from_date"], dayfirst=True)
    splitted_dates["to_date"] = pd.to_datetime(splitted_dates["to_date"], dayfirst=True)
    vak_list[["from_date", "to_date"]] = splitted_dates[["from_date", "to_date"]]
    vak_list.drop("included_date", axis=1, inplace=True)
    # replace \n in names
    vak_list.name = vak_list.name.str.replace('\n', '')
    # split out by specialties
    vak_list.loc[:, "specialties"] = vak_list["specialties"].str.findall(r"\d+\.\d+\.\d+")
    vak_list = vak_list.explode('specialties').reset_index()
    # Process merged/empty cells
    vak_list.ffill(inplace=True)
    # Format id
    vak_list.id = vak_list.id.str[:-1].astype(int)
    vak_list.to_parquet(Path("data") / "vak_journals.parquet")


if __name__ == "__main__":
    parse_vak()
