from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

# Cache last good values in memory
_last_valid_values = {}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    return True

async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    override_to_celsius = config_entry.options.get("use_celsius", True)
    entities = [
        SpaTemperatureSensor(coordinator, override_to_celsius),
        SpaDesiredTempSensor(coordinator, override_to_celsius),
        SpaCleanupCycleSensor(coordinator),
        SpaErrorCodeSensor(coordinator),
        SpaMessageSeveritySensor(coordinator),
        SpaOnlineStatusSensor(coordinator),
        SpaHeaterModeSensor(coordinator),
        SpaRunModeSensor(coordinator)
    ]

    for component in coordinator.data.get("currentState", {}).get("components", []):
        name = component.get("name")
        component_type = component.get("componentType")
        value = component.get("value")
        port = component.get("port")

        if value is not None:
            entities.append(SpaComponentSensor(coordinator, name, component_type, port))

    async_add_entities(entities)

class SpaTemperatureSensor(CoordinatorEntity):
    def __init__(self, coordinator, force_celsius):
        super().__init__(coordinator)
        self._attr_name = "Spa Water Temperature"
        self._attr_unique_id = "spa_water_temperature"
        self._force_celsius = force_celsius

    @property
    def state(self):
        raw = self.coordinator.data["currentState"]["currentTemp"]
        try:
            temp = float(raw)
            if temp <= 1.0:
                raise ValueError("invalid temp")
            if self._force_celsius and temp > 70:
                temp = (temp - 32) * 5 / 9
            _last_valid_values[self.unique_id] = round(temp, 1)
        except Exception:
            return _last_valid_values.get(self.unique_id)
        return _last_valid_values[self.unique_id]

    @property
    def unit_of_measurement(self):
        return "°C" if self._force_celsius else "°F"

class SpaDesiredTempSensor(CoordinatorEntity):
    def __init__(self, coordinator, force_celsius):
        super().__init__(coordinator)
        self._attr_name = "Spa Desired Temperature"
        self._attr_unique_id = "spa_desired_temperature"
        self._force_celsius = force_celsius

    @property
    def state(self):
        raw = self.coordinator.data["currentState"]["desiredTemp"]
        try:
            temp = float(raw)
            if temp <= 1.0:
                raise ValueError("invalid temp")
            if self._force_celsius and temp > 70:
                temp = (temp - 32) * 5 / 9
            _last_valid_values[self.unique_id] = round(temp, 1)
        except Exception:
            return _last_valid_values.get(self.unique_id)
        return _last_valid_values[self.unique_id]

    @property
    def unit_of_measurement(self):
        return "°C" if self._force_celsius else "°F"

class SpaCleanupCycleSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Spa Cleanup Cycle"
        self._attr_unique_id = "spa_cleanup_cycle"

    @property
    def state(self):
        return self.coordinator.data["currentState"].get("cleanupCycle")

class SpaErrorCodeSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Spa Error Code"
        self._attr_unique_id = "spa_error_code"

    @property
    def state(self):
        return self.coordinator.data["currentState"].get("errorCode")

class SpaMessageSeveritySensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Spa Message Severity"
        self._attr_unique_id = "spa_message_severity"

    @property
    def state(self):
        return self.coordinator.data["currentState"].get("messageSeverity")

class SpaOnlineStatusSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Spa Online Status"
        self._attr_unique_id = "spa_online_status"

    @property
    def state(self):
        return self.coordinator.data["currentState"].get("online")

class SpaHeaterModeSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Spa Heater Mode"
        self._attr_unique_id = "spa_heater_mode"

    @property
    def state(self):
        return self.coordinator.data["currentState"].get("heaterMode")

class SpaRunModeSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Spa Run Mode"
        self._attr_unique_id = "spa_run_mode"

    @property
    def state(self):
        return self.coordinator.data["currentState"].get("runMode")

class SpaComponentSensor(CoordinatorEntity):
    def __init__(self, coordinator, name, component_type, port):
        super().__init__(coordinator)
        self._attr_name = f"Spa {name} (Port {port})" if port else f"Spa {name}"
        self._attr_unique_id = f"spa_component_{component_type.lower()}_{port or 'main'}"
        self._component_name = name
        self._component_type = component_type
        self._component_port = port

    @property
    def state(self):
        for comp in self.coordinator.data["currentState"].get("components", []):
            if comp.get("componentType") == self._component_type and comp.get("port") == self._component_port:
                return comp.get("value")
        return None

