"""
tests/test_normalizers.py
--------------------------
Unit tests for city, category, and skill normalization.
"""

import pandas as pd
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_processing.normalizers import (
    normalize_city,
    normalize_category,
    normalize_skill,
    normalize_skills_column,
    normalize_location_column,
)


class TestNormalizeCity:
    def test_lowercase_lahore(self):
        assert normalize_city("lahore") == "Lahore"

    def test_alias_lhr(self):
        assert normalize_city("lhr") == "Lahore"

    def test_alias_isb(self):
        assert normalize_city("isb") == "Islamabad"

    def test_remote_keyword(self):
        assert normalize_city("remote") == "Remote"

    def test_work_from_home(self):
        assert normalize_city("work from home") == "Remote"

    def test_unknown_city_returned_as_is(self):
        assert normalize_city("MadeUpCity") == "MadeUpCity"

    def test_case_insensitive(self):
        assert normalize_city("KARACHI") == "Karachi"


class TestNormalizeCategory:
    def test_data_science(self):
        assert normalize_category("data science") == "Data Science"

    def test_ml_alias(self):
        assert normalize_category("machine learning") == "Machine Learning"

    def test_qa_alias(self):
        assert normalize_category("qa") == "Quality Assurance"

    def test_unknown_category_returned_as_is(self):
        assert normalize_category("Quantum Computing") == "Quantum Computing"


class TestNormalizeSkill:
    def test_python_alias_py(self):
        assert normalize_skill("py") == "Python"

    def test_nodejs_alias(self):
        assert normalize_skill("nodejs") == "Node.js"

    def test_k8s_alias(self):
        assert normalize_skill("k8s") == "Kubernetes"

    def test_case_insensitive_sklearn(self):
        assert normalize_skill("sklearn") == "Scikit-learn"

    def test_unknown_skill_returned_stripped(self):
        assert normalize_skill("  MyCustomSkill  ") == "MyCustomSkill"


class TestNormalizeSkillsColumn:
    def test_pipe_separated_skills_are_normalized(self):
        df = pd.DataFrame({"skills": ["py|nodejs|k8s", "sklearn|tensorflow"]})
        result = normalize_skills_column(df)
        assert result.loc[0, "skills"] == "Python|Node.js|Kubernetes"
        assert result.loc[1, "skills"] == "Scikit-learn|TensorFlow"

    def test_missing_skills_remain_nan(self):
        df = pd.DataFrame({"skills": [None, "Python"]})
        result = normalize_skills_column(df)
        assert pd.isna(result.loc[0, "skills"])

    def test_missing_column_is_ignored(self):
        df = pd.DataFrame({"other_col": [1, 2]})
        result = normalize_skills_column(df)
        assert "skills" not in result.columns


class TestNormalizeLocationColumn:
    def test_all_rows_normalized(self):
        df = pd.DataFrame({"location": ["lahore", "isb", "khi", "remote"]})
        result = normalize_location_column(df)
        assert result["location"].tolist() == ["Lahore", "Islamabad", "Karachi", "Remote"]

    def test_missing_location_remains_nan(self):
        df = pd.DataFrame({"location": [None, "lahore"]})
        result = normalize_location_column(df)
        assert pd.isna(result.loc[0, "location"])
        assert result.loc[1, "location"] == "Lahore"
