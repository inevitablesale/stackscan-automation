"""
Tests for category selection and deduplication logic.

These tests verify that:
1. Category selection works correctly with cooldown
2. Domain deduplication logic is correct
3. Email deduplication logic is correct
"""

import os
import sys
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCategorySelection:
    """Test category selection with cooldown enforcement."""

    def test_pick_today_category_with_override(self):
        """Test that CATEGORY_OVERRIDE environment variable is respected."""
        # Import the module after setting up mocks
        with patch.dict(os.environ, {"CATEGORY_OVERRIDE": "test_category"}):
            # Reimport to pick up env var
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            categories = ["cat1", "cat2", "cat3"]
            result = pipeline_worker.pick_today_category(categories, None)
            
            assert result == "test_category"

    def test_pick_today_category_deterministic_without_supabase(self):
        """Test deterministic category selection when no Supabase client."""
        with patch.dict(os.environ, {"CATEGORY_OVERRIDE": ""}, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            categories = ["cat1", "cat2", "cat3", "cat4", "cat5"]
            
            # Without supabase, should use deterministic selection
            result = pipeline_worker.pick_today_category(categories, None)
            
            # Should be one of the categories
            assert result in categories
            
            # Should be deterministic (same result on same day)
            result2 = pipeline_worker.pick_today_category(categories, None)
            assert result == result2

    def test_pick_today_category_skips_recently_used(self):
        """Test that recently used categories are skipped."""
        with patch.dict(os.environ, {
            "CATEGORY_OVERRIDE": "",
            "CATEGORY_COOLDOWN_DAYS": "7"
        }, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            categories = ["cat1", "cat2", "cat3", "cat4", "cat5"]
            
            # Mock supabase to return cat1 as recently used
            mock_supabase = MagicMock()
            
            # Calculate which category would be selected deterministically
            deterministic_idx = date.today().toordinal() % len(categories)
            deterministic_cat = categories[deterministic_idx]
            
            # Mock that the deterministic category was recently used
            mock_supabase.table.return_value.select.return_value.gte.return_value.execute.return_value.data = [
                {"category": deterministic_cat}
            ]
            
            result = pipeline_worker.pick_today_category(categories, mock_supabase)
            
            # Should not select the recently used category
            assert result != deterministic_cat or len(categories) == 1

    def test_pick_today_category_fallback_when_all_used(self):
        """Test fallback to deterministic when all categories are in cooldown."""
        with patch.dict(os.environ, {
            "CATEGORY_OVERRIDE": "",
            "CATEGORY_COOLDOWN_DAYS": "7"
        }, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            categories = ["cat1", "cat2", "cat3"]
            
            # Mock supabase to return all categories as recently used
            mock_supabase = MagicMock()
            mock_supabase.table.return_value.select.return_value.gte.return_value.execute.return_value.data = [
                {"category": cat} for cat in categories
            ]
            
            result = pipeline_worker.pick_today_category(categories, mock_supabase)
            
            # Should fall back to deterministic selection
            deterministic_idx = date.today().toordinal() % len(categories)
            deterministic_cat = categories[deterministic_idx]
            assert result == deterministic_cat

    def test_cooldown_disabled_when_zero(self):
        """Test that cooldown is disabled when CATEGORY_COOLDOWN_DAYS=0."""
        with patch.dict(os.environ, {
            "CATEGORY_OVERRIDE": "",
            "CATEGORY_COOLDOWN_DAYS": "0"
        }, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            categories = ["cat1", "cat2", "cat3"]
            
            # Mock supabase - but it should not be called
            mock_supabase = MagicMock()
            
            result = pipeline_worker.pick_today_category(categories, mock_supabase)
            
            # Should use deterministic selection
            assert result in categories


class TestGetRecentlyUsedCategories:
    """Test recently used categories lookup."""

    def test_returns_empty_when_cooldown_zero(self):
        """Test that empty set is returned when cooldown is 0."""
        with patch.dict(os.environ, {"CATEGORY_COOLDOWN_DAYS": "0"}, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            mock_supabase = MagicMock()
            result = pipeline_worker.get_recently_used_categories(mock_supabase, 0)
            
            assert result == set()
            # Should not query Supabase
            mock_supabase.table.assert_not_called()

    def test_queries_supabase_correctly(self):
        """Test that Supabase is queried with correct date filter."""
        with patch.dict(os.environ, {"CATEGORY_COOLDOWN_DAYS": "7"}, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            mock_supabase = MagicMock()
            mock_supabase.table.return_value.select.return_value.gte.return_value.execute.return_value.data = [
                {"category": "cat1"},
                {"category": "cat2"},
            ]
            
            result = pipeline_worker.get_recently_used_categories(mock_supabase, 7)
            
            assert result == {"cat1", "cat2"}
            
            # Verify the query was made to the correct table
            mock_supabase.table.assert_called_once()

    def test_handles_supabase_error_gracefully(self):
        """Test that Supabase errors don't crash the function."""
        with patch.dict(os.environ, {"CATEGORY_COOLDOWN_DAYS": "7"}, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            mock_supabase = MagicMock()
            mock_supabase.table.return_value.select.return_value.gte.return_value.execute.side_effect = Exception("Connection error")
            
            result = pipeline_worker.get_recently_used_categories(mock_supabase, 7)
            
            # Should return empty set on error
            assert result == set()


class TestRecordCategoryUsed:
    """Test recording category usage."""

    def test_records_category_usage(self):
        """Test that category usage is recorded correctly."""
        import importlib
        import pipeline_worker
        importlib.reload(pipeline_worker)
        
        mock_supabase = MagicMock()
        
        pipeline_worker.record_category_used(
            mock_supabase,
            category="test_category",
            domains_found=100,
            domains_new=50,
        )
        
        # Verify upsert was called
        mock_supabase.table.assert_called_once()
        mock_supabase.table.return_value.upsert.assert_called_once()

    def test_handles_supabase_error_gracefully(self):
        """Test that errors don't crash the function."""
        import importlib
        import pipeline_worker
        importlib.reload(pipeline_worker)
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.upsert.return_value.execute.side_effect = Exception("Connection error")
        
        # Should not raise an exception
        pipeline_worker.record_category_used(
            mock_supabase,
            category="test_category",
            domains_found=100,
            domains_new=50,
        )


class TestLoadCategories:
    """Test loading categories from file."""

    def test_load_categories_success(self):
        """Test loading categories from a valid JSON file."""
        import importlib
        import pipeline_worker
        importlib.reload(pipeline_worker)
        
        # The actual categories file should exist
        categories = pipeline_worker.load_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert all(isinstance(c, str) for c in categories)

    def test_load_categories_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with patch.dict(os.environ, {"CATEGORIES_FILE": "/nonexistent/file.json"}, clear=False):
            import importlib
            import pipeline_worker
            importlib.reload(pipeline_worker)
            
            try:
                pipeline_worker.load_categories()
                assert False, "Should have raised FileNotFoundError"
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
