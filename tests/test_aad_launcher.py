import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from importlib.util import spec_from_file_location, module_from_spec


def load_aad():
    path = Path("plugins/aiassitrequreimentdev/scripts/aad.py")
    spec = spec_from_file_location("aad_launcher", path)
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class AadLauncherTests(unittest.TestCase):
    def test_plugin_root_from_script(self):
        aad = load_aad()
        script = Path("plugins/aiassitrequreimentdev/scripts/aad.py").resolve()
        root = aad.plugin_root_from(script)
        self.assertTrue((root / "plugin.json").is_file() or root.name == "aiassitrequreimentdev")

    def test_repo_root_detected_in_monorepo(self):
        aad = load_aad()
        plugin = Path("plugins/aiassitrequreimentdev").resolve()
        repo = aad.repo_root_from_plugin(plugin)
        self.assertIsNotNone(repo)
        self.assertTrue((repo / "aiassitrequreimentdev" / "__init__.py").is_file())

    def test_ensure_package_skips_when_importable(self):
        aad = load_aad()
        runner = mock.Mock()
        with mock.patch.object(aad, "package_importable", return_value=True):
            aad.ensure_package(plugin_root=Path("plugins/aiassitrequreimentdev"), runner=runner)
        runner.assert_not_called()

    def test_ensure_package_editable_when_not_importable_and_repo_detected(self):
        aad = load_aad()
        runner = mock.Mock()
        repo = Path("D:/repo/AiAssitRequreimentDev")
        with mock.patch.object(aad, "package_importable", return_value=False), mock.patch.object(
            aad, "repo_root_from_plugin", return_value=repo
        ):
            aad.ensure_package(plugin_root=Path("plugins/aiassitrequreimentdev"), runner=runner)
        runner.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-e", str(repo)]
        )

    def test_remote_url_gets_single_git_plus_prefix(self):
        aad = load_aad()
        runner = mock.Mock()
        plugin = Path("plugins/marketplace-only")
        https = "https://git.example/org/repo.git"
        with mock.patch.object(aad, "package_importable", return_value=False), mock.patch.object(
            aad, "repo_root_from_plugin", return_value=None
        ), mock.patch.dict(
            os.environ, {"AAD_GIT_REMOTE": https, "AAD_GIT_REF": "master"}, clear=False
        ):
            aad.ensure_package(plugin_root=plugin, runner=runner)
        spec = runner.call_args[0][0][-1]
        self.assertEqual(
            spec,
            "git+https://git.example/org/repo.git@master#egg=aiassitrequreimentdev",
        )
        self.assertEqual(spec.count("git+"), 1)
        self.assertFalse(spec.startswith("git+git+"))

        runner.reset_mock()
        already = "git+https://git.example/org/repo.git@dev#egg=aiassitrequreimentdev"
        with mock.patch.object(aad, "package_importable", return_value=False), mock.patch.object(
            aad, "repo_root_from_plugin", return_value=None
        ), mock.patch.dict(
            os.environ, {"AAD_GIT_REMOTE": already, "AAD_GIT_REF": "master"}, clear=False
        ):
            aad.ensure_package(plugin_root=plugin, runner=runner)
        spec_as_is = runner.call_args[0][0][-1]
        self.assertEqual(spec_as_is, already)
        self.assertEqual(spec_as_is.count("git+"), 1)

    def test_missing_remote_documents_forms_and_install_hints(self):
        aad = load_aad()
        with mock.patch.object(aad, "package_importable", return_value=False), mock.patch.object(
            aad, "repo_root_from_plugin", return_value=None
        ), mock.patch.dict(os.environ, {"AAD_GIT_REMOTE": ""}, clear=False):
            with self.assertRaises(SystemExit) as ctx:
                aad.ensure_package(plugin_root=Path("plugins/marketplace-only"), runner=mock.Mock())
        text = str(ctx.exception)
        self.assertIn("Python", text)
        self.assertIn("https://", text)
        self.assertIn("git+", text)
        self.assertIn("公司", text)
        self.assertIn("wheel", text.lower())

    def test_pip_failure_includes_python_pypi_and_wheel(self):
        aad = load_aad()
        runner = mock.Mock(side_effect=subprocess.CalledProcessError(1, ["pip"]))
        repo = Path("D:/repo/AiAssitRequreimentDev")
        with mock.patch.object(aad, "package_importable", return_value=False), mock.patch.object(
            aad, "repo_root_from_plugin", return_value=repo
        ):
            with self.assertRaises(SystemExit) as ctx:
                aad.ensure_package(plugin_root=Path("plugins/aiassitrequreimentdev"), runner=runner)
        text = str(ctx.exception)
        self.assertIn("Python", text)
        self.assertIn("公司", text)
        self.assertIn("wheel", text.lower())

    def test_main_reexecs_after_install_when_package_was_missing(self):
        aad = load_aad()
        exec_fn = mock.Mock()
        with mock.patch.object(aad, "ensure_package", return_value=True), mock.patch.dict(
            os.environ, {}, clear=False
        ):
            os.environ.pop("AAD_BOOTSTRAPPED", None)
            code = aad.main(["check", "features/X", "--gate", "G1"], exec_fn=exec_fn)
            self.assertEqual(os.environ.get("AAD_BOOTSTRAPPED"), "1")
        self.assertEqual(code, 0)
        exec_fn.assert_called_once()
        program, argv = exec_fn.call_args[0]
        self.assertEqual(program, sys.executable)
        self.assertEqual(argv[0], sys.executable)
        self.assertTrue(str(argv[1]).endswith("aad.py"))
        self.assertEqual(argv[2:], ["check", "features/X", "--gate", "G1"])

    def test_main_errors_when_still_not_importable_after_reexec(self):
        aad = load_aad()
        with mock.patch.object(aad, "package_importable", return_value=False), mock.patch.object(
            aad, "ensure_package", side_effect=AssertionError("must not pip after reexec")
        ), mock.patch.dict(os.environ, {"AAD_BOOTSTRAPPED": "1"}, clear=False):
            with self.assertRaises(SystemExit) as ctx:
                aad.main(["check"])
        text = str(ctx.exception)
        self.assertIn("Python", text)
        self.assertIn("公司", text)
        self.assertIn("wheel", text.lower())


if __name__ == "__main__":
    unittest.main()
