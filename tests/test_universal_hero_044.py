"""Regression checks for Cricky universal See All category hero, v0.4.4 RC.

No Kodi install, tokens, network access or third-party modules required.
Run: python -m unittest discover -s tests -p 'test_universal_hero_044.py'
"""
import ast
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
STREAM_ZIP = ROOT / "plugin.video.streamrow-0.3.1-RC.zip"
HOME_ZIP = ROOT / "plugin.video.tvstreaming.homepersonalisation-0.1.4-RC.zip"


class FakeListItem:
    def __init__(self, label="", offscreen=False):
        self.label = label
        self.info = {}
        self.art = {}
        self.properties = {}
        self.context = []

    def setArt(self, art):
        self.art.update(art)

    def setInfo(self, kind, info):
        assert kind == "video"
        self.info.update(info)

    def setProperty(self, key, value):
        self.properties[key] = value

    def addContextMenuItems(self, items):
        self.context += items


class FakePlugin:
    def __init__(self):
        self.rows = []

    def addDirectoryItem(self, handle, url, item, isFolder):
        self.rows.append((handle, url, item, isFolder))


def extracted_functions(source, *names):
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name in names]
    assert len(nodes) == len(names), (names, [n.name for n in nodes])
    return compile(ast.Module(body=nodes, type_ignores=[]), "<extracted-kodi>", "exec")


class UniversalHeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(STREAM_ZIP) as z:
            cls.stream_zip_names = z.namelist()
            assert z.testzip() is None
            cls.stream = z.read("plugin.video.streamrow/default.py").decode("utf-8")
            cls.stream_xml = z.read("plugin.video.streamrow/addon.xml")
            cls.stream_media = z.read(
                "plugin.video.streamrow/resources/media/see_all_miami_neutral_v024.png")
        with ZipFile(HOME_ZIP) as z:
            cls.home_zip_names = z.namelist()
            assert z.testzip() is None
            cls.home = z.read("plugin.video.tvstreaming.homepersonalisation/default.py").decode("utf-8")
            cls.home_xml = z.read("plugin.video.tvstreaming.homepersonalisation/addon.xml")

    def test_zip_compatibility_and_source_parity(self):
        self.assertEqual(ET.fromstring(self.stream_xml).get("version"), "0.3.1")
        self.assertEqual(ET.fromstring(self.home_xml).get("version"), "0.1.4")
        self.assertEqual(self.stream, (ROOT / "src/streamrow/default.py").read_text(encoding="utf-8"))
        self.assertEqual(self.home, (ROOT / "src/homepersonalisation/default.py").read_text(encoding="utf-8"))
        compile(self.stream, "streamrow/default.py", "exec")
        compile(self.home, "homepersonalisation/default.py", "exec")
        self.assertTrue(self.stream_media.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_streamrow_title_normalisation(self):
        ns = {"re": re, "CATEGORIES": {"action": ("Action", "movie", 28)}}
        exec(extracted_functions(self.stream, "category_hero_title"), ns)
        hero = ns["category_hero_title"]
        for label, expected in (
            ("Netflix Movies", "Netflix Movies"),
            ("Disney+ Series", "Disney+ Series"),
            ("Trending Movies", "Trending Movies"),
            ("Action — See All First", "Action"),
            ("See All - Comedy Movies", "Comedy Movies"),
            ("[COLOR white]Documentaries[/COLOR]", "Documentaries"),
        ):
            with self.subTest(label=label):
                self.assertEqual(hero({"title": label}, "action"), expected)
        self.assertEqual(hero(None, "action"), "Action")

    def test_streamrow_category_hero_without_first_title_metadata(self):
        plugin = FakePlugin()
        ns = {
            "re": re,
            "CATEGORIES": {"action": ("Action", "movie", 28)},
            "xbmcgui": type("G", (), {"ListItem": FakeListItem}),
            "xbmcplugin": plugin,
        }
        exec(extracted_functions(self.stream,
                                 "category_hero_title", "featured_info", "add_see_all"), ns)
        first = {"title": "Film One", "label": "Film One",
                 "plot": "A film-specific synopsis",
                 "fanart": "fanart://first", "rating": 9}
        ns["add_see_all"](21, "neutral://icon", "action", first,
                          "safetoken", {"title": "Netflix Movies", "media": "movie"})
        self.assertEqual(len(plugin.rows), 1)
        _, url, item, folder = plugin.rows[0]
        self.assertFalse(folder)
        self.assertEqual(url, "plugin://plugin.video.streamrow/?mode=launch&source=safetoken")
        self.assertEqual(item.label, "See All")
        self.assertEqual(item.info["title"], "Netflix Movies")
        self.assertEqual(item.info["plot"], "")
        self.assertEqual(item.art["poster"], "neutral://icon")
        self.assertEqual(item.art["fanart"], "fanart://first")
        self.assertEqual(item.properties["streamrow.type"], "see_all")
        self.assertEqual(item.properties["IsPlayable"], "false")
        self.assertNotIn("Film One", str(item.info))
        self.assertNotIn("film-specific synopsis", str(item.info))

    def test_mixed_feed_hero_title_and_other_folders_untouched(self):
        plugin = FakePlugin()
        ns = {
            "xbmcgui": type("G", (), {"ListItem": FakeListItem}),
            "xbmcplugin": plugin,
        }
        exec(extracted_functions(self.home, "add_folder"), ns)
        ns["add_folder"](11, "See All - Recommended For You", "plugin://feed",
                         {"poster": "neutral", "fanart": "hero-backdrop"},
                         "Browse movies and TV...", {"override_landscape": "neutral"},
                         hero_title="Recommended For You")
        ns["add_folder"](11, "Next Page", "plugin://next", plot="More entries")
        self.assertEqual(plugin.rows[0][2].info, {
            "title": "Recommended For You", "plot": ""})
        self.assertEqual(plugin.rows[0][2].art["poster"], "neutral")
        self.assertEqual(plugin.rows[0][2].art["fanart"], "hero-backdrop")
        self.assertEqual(plugin.rows[0][2].properties["override_landscape"], "neutral")
        self.assertEqual(plugin.rows[1][2].info, {
            "title": "Next Page", "plot": "More entries"})

    def test_unchanged_core_paths_and_exact_categories(self):
        self.assertIn("hero_title=core.LABEL_BY_KIND[kind]", self.home)
        self.assertIn("show_movie_tv_item(handle, media, entry)", self.home)
        self.assertIn("xbmc.executebuiltin(command)", self.stream)
        self.assertIn("first_title, source_token, meta", self.stream)
        self.assertIn("def listing(handle, category, source_token=None)", self.stream)
        self.assertIn("def cleanup_duplicates():", self.home)
        self.assertIn("def apply_poster_style():", self.home)
        self.assertIn("neutral_see_all_art()", self.home)


if __name__ == "__main__":
    unittest.main()
