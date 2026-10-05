"""
Automated Skill Verification Suite for Z.O.E.
=============================================
Students should run this test script before committing or opening a Pull Request:
    python3 test_skills.py

All tests must pass (OK) to guarantee that new capabilities work cleanly
and do not break existing features.
"""

import unittest
from skill_manager import SkillManager
from skills.base_skill import BaseSkill


class TestZoeSkills(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the SkillManager once for all tests."""
        cls.manager = SkillManager()

    def test_01_skills_loaded(self):
        """Verify that skills are discovered and loaded."""
        self.assertGreater(len(self.manager.skills), 0, "No skills were loaded from the skills/ directory.")
        print(f"\n[TEST PASS] Loaded {len(self.manager.skills)} capabilities successfully.")

    def test_02_base_skill_compliance(self):
        """Verify that all skills follow the BaseSkill contract."""
        for skill in self.manager.skills:
            self.assertIsInstance(skill, BaseSkill, f"{skill} must inherit from BaseSkill.")
            self.assertTrue(hasattr(skill, "name") and skill.name, f"{skill} must have a non-empty name.")
            self.assertTrue(hasattr(skill, "description") and skill.description, f"{skill.name} must have a description.")
            self.assertIsInstance(skill.triggers, list, f"{skill.name} triggers must be a list.")
            self.assertTrue(hasattr(skill, "author") and skill.author, f"{skill.name} must specify an author.")
            self.assertTrue(hasattr(skill, "version") and skill.version, f"{skill.name} must have a version string.")

    def test_03_calculator_skill(self):
        """Verify calculator arithmetic and unit conversions."""
        res_calc = self.manager.route_message("what is 25 * 4?")
        self.assertIsNotNone(res_calc, "Calculator did not trigger on 'what is 25 * 4?'")
        skill, reply = res_calc
        self.assertIn("100", reply, "Calculator calculation for 25 * 4 failed.")

        res_temp = self.manager.route_message("convert 0 celsius to fahrenheit")
        self.assertIsNotNone(res_temp, "Calculator did not trigger on temperature conversion.")
        _, reply_temp = res_temp
        self.assertIn("32", reply_temp, "Celsius to Fahrenheit conversion failed.")

    def test_04_oris_retail_skill(self):
        """Verify Project ORIS retail FAQs and order tracking."""
        # Test order tracking
        res_order = self.manager.route_message("please track order ORIS-1002")
        self.assertIsNotNone(res_order, "ORIS skill did not trigger on order tracking query.")
        _, reply_order = res_order
        self.assertIn("ORIS-1002", reply_order)
        self.assertIn("In Transit", reply_order)

        # Test returns policy
        res_return = self.manager.route_message("what is your return policy?")
        self.assertIsNotNone(res_return, "ORIS skill did not trigger on returns inquiry.")
        _, reply_return = res_return
        self.assertIn("30-day", reply_return)

    def test_05_weather_skill(self):
        """Verify weather skill triggers and returns a location report."""
        res_weather = self.manager.route_message("what is the weather in London?")
        self.assertIsNotNone(res_weather, "Weather skill did not trigger on 'weather in London'.")
        _, reply_weather = res_weather
        self.assertTrue("London" in reply_weather or "weather" in reply_weather.lower())

    def test_06_student_template_skill(self):
        """Verify the template skill executes safely."""
        res_tmpl = self.manager.route_message("test sample capability")
        self.assertIsNotNone(res_tmpl, "Student template skill did not trigger.")
        _, reply_tmpl = res_tmpl
        self.assertIn("Student Template Skill", reply_tmpl)

    def test_07_resilience_to_empty_and_unknown_queries(self):
        """Verify that unknown queries return None without crashing."""
        self.assertIsNone(self.manager.route_message(""))
        self.assertIsNone(self.manager.route_message("   "))
        self.assertIsNone(self.manager.route_message("xyzabcrandomunhandledphrase12345"))


if __name__ == "__main__":
    unittest.main()
