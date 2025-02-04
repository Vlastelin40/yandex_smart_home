from __future__ import annotations

from typing import Type

from homeassistant.components import binary_sensor, input_text, sensor
from homeassistant.const import ATTR_DEVICE_CLASS, STATE_OFF, STATE_ON
from homeassistant.core import State
import pytest

from custom_components.yandex_smart_home import const
from custom_components.yandex_smart_home.error import SmartHomeError
from custom_components.yandex_smart_home.prop import PROPERTIES
from custom_components.yandex_smart_home.prop_event import PROPERTY_EVENT, EventProperty
from custom_components.yandex_smart_home.prop_float import PROPERTY_FLOAT

from . import BASIC_CONFIG, MockConfig
from .test_prop import assert_no_properties, get_exact_one_property


class ConfigNoBeta(MockConfig):
    @property
    def beta(self):
        return False


class MockEventProperty(EventProperty):
    def supported(self) -> bool:
        return True


async def test_property_event(hass):
    prop = MockEventProperty(hass, BASIC_CONFIG, State('state.test', STATE_ON))
    with pytest.raises(SmartHomeError) as e:
        prop.get_value()
    assert e.value.code == const.ERR_NOT_SUPPORTED_IN_CURRENT_MODE
    assert 'Failed to get' in e.value.message


@pytest.mark.parametrize('prop', [p for p in PROPERTIES if issubclass(p, EventProperty)])
async def test_property_event_no_beta(hass, prop: Type[EventProperty]):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: binary_sensor.DEVICE_CLASS_DOOR,
    })
    assert prop(hass, ConfigNoBeta(), state).supported() is False


@pytest.mark.parametrize('device_class,supported', [
    (binary_sensor.DEVICE_CLASS_DOOR, True),
    (binary_sensor.DEVICE_CLASS_GARAGE_DOOR, True),
    (binary_sensor.DEVICE_CLASS_WINDOW, True),
    (binary_sensor.DEVICE_CLASS_OPENING, True),
    (binary_sensor.DEVICE_CLASS_BATTERY, False),
])
async def test_property_event_contact(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_OPEN)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_OPEN)
        return

    assert prop.retrievable
    assert prop.parameters() == {'events': [{'value': 'opened'}, {'value': 'closed'}], 'instance': 'open'}
    assert prop.get_value() == 'opened'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'closed'


@pytest.mark.parametrize('device_class,supported', [
    (binary_sensor.DEVICE_CLASS_MOTION, True),
    (binary_sensor.DEVICE_CLASS_OCCUPANCY, True),
    (binary_sensor.DEVICE_CLASS_PRESENCE, True),
    (binary_sensor.DEVICE_CLASS_BATTERY, False),
])
async def test_property_event_motion(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_MOTION)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_OPEN)
        return

    assert prop.retrievable
    assert prop.parameters() == {'events': [{'value': 'detected'}, {'value': 'not_detected'}], 'instance': 'motion'}
    assert prop.get_value() == 'detected'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'not_detected'


@pytest.mark.parametrize('device_class,supported', [
    (binary_sensor.DEVICE_CLASS_GAS, True),
    (binary_sensor.DEVICE_CLASS_BATTERY, False),
])
async def test_property_event_gas(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_GAS)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_GAS)
        return

    assert prop.retrievable
    assert prop.parameters() == {
        'events': [{'value': 'detected'}, {'value': 'not_detected'}, {'value': 'high'}], 'instance': 'gas'
    }
    assert prop.get_value() == 'detected'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'not_detected'
    prop.state.state = 'high'
    assert prop.get_value() == 'high'


@pytest.mark.parametrize('device_class,supported', [
    (binary_sensor.DEVICE_CLASS_SMOKE, True),
    (binary_sensor.DEVICE_CLASS_BATTERY, False),
])
async def test_property_event_smoke(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_SMOKE)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_SMOKE)
        return

    assert prop.retrievable
    assert prop.parameters() == {
        'events': [{'value': 'detected'}, {'value': 'not_detected'}, {'value': 'high'}], 'instance': 'smoke'
    }
    assert prop.get_value() == 'detected'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'not_detected'
    prop.state.state = 'high'
    assert prop.get_value() == 'high'


@pytest.mark.parametrize('device_class,supported', [
    (binary_sensor.DEVICE_CLASS_BATTERY, True),
    (binary_sensor.DEVICE_CLASS_SMOKE, False),
])
async def test_property_event_battery(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_BATTERY_LEVEL)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_BATTERY_LEVEL)
        return

    assert prop.retrievable
    assert prop.parameters() == {
        'events': [{'value': 'low'}, {'value': 'normal'}], 'instance': 'battery_level'
    }
    assert prop.get_value() == 'low'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'normal'


@pytest.mark.parametrize('device_class,supported', [
    ('water_level', True),
    (binary_sensor.DEVICE_CLASS_SMOKE, False),
])
async def test_property_event_water_level(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_FLOAT, const.EVENT_INSTANCE_WATER_LEVEL)
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_WATER_LEVEL)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_WATER_LEVEL)
        return

    assert prop.retrievable
    assert prop.parameters() == {
        'events': [{'value': 'low'}, {'value': 'normal'}], 'instance': 'water_level'
    }
    assert prop.get_value() == 'low'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'normal'


@pytest.mark.parametrize('device_class,supported', [
    (binary_sensor.DEVICE_CLASS_MOISTURE, True),
    (binary_sensor.DEVICE_CLASS_SMOKE, False),
])
async def test_property_event_water_leak(hass, device_class, supported):
    state = State('binary_sensor.test', binary_sensor.STATE_ON, {
        ATTR_DEVICE_CLASS: device_class
    })
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_WATER_LEAK)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_WATER_LEAK)
        return

    assert prop.retrievable
    assert prop.parameters() == {
        'events': [{'value': 'leak'}, {'value': 'dry'}], 'instance': 'water_leak'
    }
    assert prop.get_value() == 'leak'
    prop.state.state = STATE_OFF
    assert prop.get_value() == 'dry'


@pytest.mark.parametrize('domain,attribute,device_class,supported', [
    (binary_sensor.DOMAIN, 'last_action', None, True),
    (sensor.DOMAIN, 'action', None, True),
    (input_text.DOMAIN, 'bar', 'button', True),
    (binary_sensor.DOMAIN, 'bar', None, False),
])
async def test_property_event_button_sensor(hass, domain, attribute, device_class, supported):
    state = State(f'{domain}.test', STATE_ON, {
        attribute: 'single',
        ATTR_DEVICE_CLASS: device_class
    })
    assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_VIBRATION)
    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_BUTTON)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_BUTTON)
        return

    if domain != input_text.DOMAIN:
        assert not prop.retrievable
        assert prop.parameters() == {
            'events': [{'value': 'click'}, {'value': 'double_click'}, {'value': 'long_press'}],
            'instance': 'button'
        }
        assert prop.get_value() == 'click'

        prop.state = State(f'{domain}.test', STATE_ON, {
            attribute: 'double'
        })
        assert prop.get_value() == 'double_click'

        prop.state = State(f'{domain}.test', STATE_ON, {
            attribute: 'hold'
        })
        assert prop.get_value() == 'long_press'

        prop.state = State(f'{domain}.test', STATE_ON, {
            attribute: 'invalid'
        })
        assert prop.get_value() is None

    prop.state = State(f'{domain}.test', 'click')
    assert prop.get_value() == 'click'


@pytest.mark.parametrize('domain,attribute,device_class,supported', [
    (binary_sensor.DOMAIN, 'last_action', None, True),
    (sensor.DOMAIN, 'action', None, True),
    (binary_sensor.DOMAIN, None, binary_sensor.DEVICE_CLASS_VIBRATION, True),
    (binary_sensor.DOMAIN, 'bar', None, False),
])
async def test_property_event_vibration_sensor(hass, domain, attribute, device_class, supported):
    attributes = {}
    if attribute:
        attributes[attribute] = 'vibrate'
    if device_class:
        attributes[ATTR_DEVICE_CLASS] = device_class

    state = State(f'{domain}.test', STATE_ON, attributes)
    assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_BUTTON)

    if supported:
        prop = get_exact_one_property(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_VIBRATION)
    else:
        assert_no_properties(hass, BASIC_CONFIG, state, PROPERTY_EVENT, const.EVENT_INSTANCE_VIBRATION)
        return

    assert not prop.retrievable
    assert prop.parameters() == {
        'events': [{'value': 'vibration'}, {'value': 'tilt'}, {'value': 'fall'}],
        'instance': 'vibration'
    }
    assert prop.get_value() == 'vibration'

    if attribute:
        prop.state = State(f'{domain}.test', STATE_ON, {
            attribute: 'flip90'
        })
        assert prop.get_value() == 'tilt'

        prop.state = State(f'{domain}.test', STATE_ON, {
            attribute: 'free_fall'
        })
        assert prop.get_value() == 'fall'

        prop.state = State(f'{domain}.test', STATE_ON, {
            attribute: 'invalid'
        })
        assert prop.get_value() is None

    if device_class:
        prop.state = State(f'{domain}.test', STATE_OFF, {
            ATTR_DEVICE_CLASS: device_class
        })
        assert prop.get_value() is None
