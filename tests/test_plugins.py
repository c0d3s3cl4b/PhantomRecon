from unittest.mock import Mock, patch

from core.plugins import discover_plugins


@patch("core.plugins._entry_points")
def test_discover_plugins_without_loading(mock_points):
    point = Mock()
    point.name = "demo"
    point.value = "demo_plugin:plugin"
    point.dist = Mock(name="demo-plugin", version="1.0.0")
    mock_points.return_value = [point]

    plugins = discover_plugins()

    assert len(plugins) == 1
    assert plugins[0].name == "demo"
    assert plugins[0].loaded is False
    point.load.assert_not_called()


@patch("core.plugins._entry_points")
def test_plugin_load_failure_is_isolated(mock_points):
    point = Mock()
    point.name = "broken"
    point.value = "broken:plugin"
    point.dist = None
    point.load.side_effect = RuntimeError("boom")
    mock_points.return_value = [point]

    plugin = discover_plugins(load=True)[0]

    assert plugin.loaded is False
    assert "RuntimeError" in plugin.error
