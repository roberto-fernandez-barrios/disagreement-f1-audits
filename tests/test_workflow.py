"""Check that the new reproducibility interface detects real regressions."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.manage import equivalent, safe_file, check_manifest, write, sha, replay_tree, MANIFEST, FROZEN


class IntegrityAndComparison(unittest.TestCase):
    def test_roundoff_is_not_a_scientific_change(self):
        equivalent({"cost": [74.59361699821036]}, {"cost": [74.59361699821037]})
        equivalent([{ "value": "0.01" }], [{ "value": "0.010000000000000002" }])

    def test_material_changes_and_schema_changes_fail(self):
        for left, right in [(0.01, 0.0101), (307200, 307201),
                            ({"all": 36}, {"reserved": 28}), ([1, 2], [1]),
                            (float("nan"), float("nan"))]:
            with self.subTest(left=left, right=right):
                with self.assertRaises(ValueError): equivalent(left, right)

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root/"reproducibility").mkdir()
            item = root/"result.txt"; item.write_bytes(b"reference")
            rec = {"sha256": sha(item), "bytes": item.stat().st_size}
            write(root/MANIFEST, {"result.txt": rec})
            write(root/FROZEN, {"files": {"old/result.txt": {"path": "result.txt", "sha256": rec["sha256"]}}})
            check_manifest(root)
            item.write_bytes(b"corrupted")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"): check_manifest(root)

    def test_outside_file_cannot_enter_a_package(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)/"inside"; base.mkdir()
            (Path(folder)/"outside.txt").write_bytes(b"not part of artifact")
            with self.assertRaisesRegex(ValueError, "unsafe"): safe_file(base, "../outside.txt")

    def test_replay_restores_historical_paths_without_changing_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for d in ("reproducibility", "tools", "data"): (root/d).mkdir()
            source = root/"data/current.txt"; source.write_bytes(b"frozen\r\nbytes")
            (root/"tools/manage.py").write_bytes(b"source")
            write(root/FROZEN, {"files": {"inputs/original.txt": {"path": "data/current.txt", "sha256": sha(source)}}})
            run = replay_tree(root)
            self.assertEqual((run/"inputs/original.txt").read_bytes(), source.read_bytes())
            (run/"inputs/original.txt").write_bytes(b"new result")
            self.assertEqual(source.read_bytes(), b"frozen\r\nbytes")

    def test_replay_rejects_escaping_historical_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root/"reproducibility").mkdir()
            write(root/FROZEN, {"files": {"../outside.txt": {"path": "unused", "sha256": "unused"}}})
            with self.assertRaisesRegex(ValueError, "Unsafe historical path"): replay_tree(root)


if __name__ == "__main__": unittest.main()
