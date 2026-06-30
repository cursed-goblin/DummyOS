import json

from omni.registry import App, AppRegistry


def test_add_get_remove(tmp_path):
    reg = AppRegistry(path=tmp_path / "apps.json")
    reg.add(App("Firefox", "linux", "flatpak run org.mozilla.firefox"))
    assert reg.get("firefox").platform == "linux"
    assert reg.remove("Firefox") is True
    assert reg.get("firefox") is None


def test_invalid_platform():
    try:
        App("Bad", "beos", "cmd")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown platform")


def test_persistence(tmp_path):
    path = tmp_path / "apps.json"
    reg = AppRegistry(path=path)
    reg.add(App("Instagram", "android", "waydroid app launch com.instagram.android"))
    data = json.loads(path.read_text())
    assert data["apps"][0]["name"] == "Instagram"
