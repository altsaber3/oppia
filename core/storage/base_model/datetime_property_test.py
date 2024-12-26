"""Tests for investigating DateTimeProperty timezone behavior."""

from __future__ import annotations

import datetime
from core.platform import models
from core.tests import test_utils

(base_models,) = models.Registry.import_models([
    models.Names.BASE_MODEL
])


class TimestampTestModel(base_models.BaseModel):
    """Model for testing timestamp behavior."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_on = kwargs.get('created_on', datetime.datetime.utcnow())

    @classmethod
    def get_deletion_policy(cls):
        return base_models.DELETION_POLICY.NOT_APPLICABLE

    @classmethod
    def has_reference_to_user_id(cls, unused_user_id):
        return False


class DateTimePropertyTests(test_utils.GenericTestBase):
    """Tests DateTimeProperty timezone handling."""

    def setUp(self):
        super().setUp()
        self.model_instance = TimestampTestModel()
        self.model_instance.put()

    def test_timezone_naive_storage(self):
        """Test storing timezone-naive timestamps."""
        naive_time = datetime.datetime.utcnow()
        test_model = TimestampTestModel(created_on=naive_time)
        test_model.put()
        
        retrieved_model = TimestampTestModel.get_by_id(test_model.id)
        self.assertIsNotNone(retrieved_model)
        self.assertEqual(retrieved_model.created_on, naive_time)
        self.assertIsNone(
            retrieved_model.created_on.tzinfo,
            msg="DateTimeProperty should preserve timezone-naive state")

    def test_timezone_aware_storage(self):
        """Test storing timezone-aware timestamps."""
        aware_time = datetime.datetime.now(datetime.timezone.utc)
        test_model = TimestampTestModel(created_on=aware_time)
        test_model.put()
        
        retrieved_model = TimestampTestModel.get_by_id(test_model.id)
        self.assertIsNotNone(retrieved_model)
        # Check if timezone information is preserved
        has_tzinfo = retrieved_model.created_on.tzinfo is not None
        self.assertTrue(
            has_tzinfo,
            msg="DateTimeProperty strips timezone info from aware timestamps")