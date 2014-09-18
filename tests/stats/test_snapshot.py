from unittest import TestCase

from metrology.stats.snapshot import Snapshot


class SnapshotTest(TestCase):
    def setUp(self):
        self.snapshot = Snapshot([5, 1, 2, 3, 4])

    def test_median(self):
        self.assertAlmostEqual(self.snapshot.median, 3, 1)

    def test_75th_percentile(self):
        self.assertAlmostEqual(self.snapshot.p75, 4.5, 1)

    def test_95th_percentile(self):
        self.assertAlmostEqual(self.snapshot.p95, 5.0, 1)

    def test_98th_percentile(self):
        self.assertAlmostEqual(self.snapshot.p98, 5.0, 1)

    def test_99th_percentile(self):
        self.assertAlmostEqual(self.snapshot.p99, 5.0, 1)

    def test_999th_percentile(self):
        self.assertAlmostEqual(self.snapshot.p999, 5.0, 1)

    def test_size(self):
        self.assertEqual(self.snapshot.size(), 5)
