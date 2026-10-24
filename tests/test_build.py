import unittest
from pathlib import Path

import build


class BuildTest(unittest.TestCase):
    def test_content_has_expected_slide_structure(self):
        content = build.load_content()
        kinds = [slide["kind"] for slide in content["slides"]]
        self.assertEqual(kinds[0], "entrance")
        self.assertEqual(kinds[-2:], ["materials", "exit"])
        self.assertGreaterEqual(kinds.count("work"), 1)

    def test_content_is_rendered_into_slide_markup(self):
        content = build.load_content()
        entrance = build.slide_html(content["slides"][0], 1, len(content["slides"]), content)
        self.assertIn(content["site"]["name"], entrance)
        self.assertIn(content["site"]["intro"], entrance)

    def test_generated_assets_exist_and_contain_both_themes(self):
        for theme in ("light", "dark"):
            output = Path(build.HERE) / f"profile-{theme}.svg"
            self.assertTrue(output.is_file())
            generated = output.read_text(encoding="utf-8")
            self.assertIn("class=\"root\"", generated)
            self.assertIn("class=\"slides\"", generated)
            self.assertIn("animation: walk", generated)


if __name__ == "__main__":
    unittest.main()
