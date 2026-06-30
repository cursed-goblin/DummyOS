from omni.agent.agent import Agent
from omni.agent.permissions import Permission, PermissionManager
from omni.registry import App, AppRegistry


def _agent(tmp_path):
    reg = AppRegistry(path=tmp_path / "apps.json")
    reg.add(App("Firefox", "linux", "true"))
    perms = PermissionManager(Permission.OPEN_APPS_FILES)
    return Agent(registry=reg, permissions=perms)


def test_plan_brightness(tmp_path):
    agent = _agent(tmp_path)
    calls = agent.plan("set brightness to 40")
    assert ("set_brightness", {"value": 40}) in calls


def test_plan_open_app(tmp_path):
    agent = _agent(tmp_path)
    calls = agent.plan("please open firefox")
    assert ("open_app", {"name": "Firefox"}) in calls


def test_chat_executes(tmp_path):
    agent = _agent(tmp_path)
    resp = agent.chat("open firefox and set brightness to 30")
    assert resp.actions
