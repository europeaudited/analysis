"""Offline tests: parsers, checksums and the LMDI helper. No internet needed.
Run: python -m unittest discover -s tests -v
"""
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.decompose import lmdi  # noqa: E402
from pipelines import ameco, ardeco, cache, eurostat  # noqa: E402


class TestEurostat(unittest.TestCase):
    def test_parse_jsonstat(self):
        obj = {
            "id": ["geo", "time"], "size": [2, 3],
            "dimension": {
                "geo": {"category": {"index": {"BE": 0, "NL": 1}}},
                "time": {"category": {"index": {"2020": 0, "2021": 1, "2022": 2}}},
            },
            "value": {"0": 1.0, "1": 2.0, "2": 3.0, "4": 5.0},
        }
        df = eurostat.parse_jsonstat(obj)
        self.assertEqual(len(df), 4)
        s = eurostat.to_series_by_geo(df)
        self.assertEqual(s["BE"], {2020: 1.0, 2021: 2.0, 2022: 3.0})
        self.assertEqual(s["NL"], {2021: 5.0})


class TestAmeco(unittest.TestCase):
    def test_parse_table(self):
        html = ("<html><table><tr><th>Country</th><th>2020</th><th>2021</th><th>2022</th></tr>"
                "<tr><td>Belgium</td><td>-9.0</td><td>-5.4</td><td>-3.5</td></tr>"
                "<tr><td>Germany</td><td>-4.4</td><td>-3.2</td><td>n.a.</td></tr></table></html>")
        df = ameco.parse_table(html)
        self.assertEqual(len(df), 6)
        be = df[df.country == "Belgium"].set_index("year").value
        self.assertEqual(be[2021], -5.4)
        self.assertTrue(math.isnan(df[(df.country == "Germany") & (df.year == 2022)].value.iloc[0]))


class TestArdeco(unittest.TestCase):
    def test_parse_csv_with_commas_in_name(self):
        text = ("NAME_HTML,TERRITORY_ID,LEVEL_ID,DATE,VERSIONS,UNIT,VALUE,YEAR\n"
                "Hainaut,BE32,2,1980-01-01,2024,Mio EUR,12345.6,1980\n"
                '"Region, with comma",XX99,2,1981-01-01,2024,Mio EUR,10.5,1981\n')
        df = ardeco.parse_csv(text)
        self.assertEqual(df.TERRITORY_ID.tolist(), ["BE32", "XX99"])
        self.assertEqual(df.NAME_HTML.iloc[1], "Region, with comma")
        self.assertEqual(float(df.VALUE.iloc[0]), 12345.6)


class TestCache(unittest.TestCase):
    def test_manifest_roundtrip_and_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            data = Path(t) / "data"
            (data / "raw").mkdir(parents=True)
            f = data / "raw" / "x.csv"
            f.write_text("a,b\n1,2\n")
            cache.write_manifest(data)
            self.assertTrue(cache.verify(data))
            self.assertEqual(cache.load_csv(f).shape, (1, 2))
            f.write_text("a,b\n1,3\n")
            with self.assertRaises(cache.ChecksumError):
                cache.verify(data)


class TestLmdi(unittest.TestCase):
    def test_terms_add_up_exactly(self):
        f0 = {"a": 2.0, "b": 5.0, "c": 0.5}
        f1 = {"a": 2.6, "b": 4.1, "c": 0.7}
        x0, x1 = 2.0 * 5.0 * 0.5, 2.6 * 4.1 * 0.7
        parts = lmdi(x0, x1, f0, f1)
        self.assertAlmostEqual(sum(parts.values()), x1 - x0, places=10)


if __name__ == "__main__":
    unittest.main()
