"""European Commission AMECO series: fetch the HTML table and parse it.

fetch_series() needs internet. UNTESTED IN SANDBOX; VALIDATED IN CI.
parse_table() is pure and is unit-tested offline on a small fixture.
"""
from html.parser import HTMLParser

import pandas as pd
import requests

URL = ("https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={code}"
       "&countries={countries}&years={years}&lastYear=0&yearorder=ASC&defaultCountries=0")


class _Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self._row, self._cell, self._in_cell = [], None, [], False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        elif tag == "tr" and self.tables:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._in_cell, self._cell = True, []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_cell:
            self._row.append("".join(self._cell).strip())
            self._in_cell = False
        elif tag == "tr" and self._row is not None and self.tables:
            if self._row:
                self.tables[-1].append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._in_cell:
            self._cell.append(data)


def parse_table(html):
    """AMECO HTML -> DataFrame with columns country, year, value. Finds the table whose
    header row contains four-digit years; the first cell of each later row is the country."""
    p = _Tables()
    p.feed(html)
    for t in p.tables:
        for i, row in enumerate(t):
            years = [(j, int(c)) for j, c in enumerate(row) if c.isdigit() and len(c) == 4]
            if len(years) >= 3:
                out = []
                for r in t[i + 1:]:
                    if not r or not r[0]:
                        continue
                    for j, y in years:
                        if j < len(r):
                            s = r[j].replace(",", "").replace("\xa0", "").strip()
                            try:
                                out.append((r[0], y, float(s)))
                            except ValueError:
                                out.append((r[0], y, float("nan")))
                return pd.DataFrame(out, columns=["country", "year", "value"])
    raise ValueError("No AMECO year table found")


def fetch_series(code, countries="BEL,NLD,DEU", years="2009-2027", timeout=120):
    """Download one AMECO series for the given countries. Untested in sandbox; validated in CI."""
    r = requests.get(URL.format(code=code, countries=countries, years=years), timeout=timeout)
    r.raise_for_status()
    df = parse_table(r.text)
    df.insert(0, "code", code)
    return df
