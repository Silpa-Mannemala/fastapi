from datetime import timedelta
from uuid import uuid4

import pytest

from app.models import DeviceResponse, DeviceStatus, DeviceType
from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.device_service import (
	DeviceAlreadyExistsError,
	DeviceNotFoundError,
	DeviceService,
)


@pytest.fixture
def service_and_repository() -> tuple[DeviceService, InMemoryDeviceRepository]:
	repository = InMemoryDeviceRepository()
	return DeviceService(repository), repository


def make_device(status: DeviceStatus = DeviceStatus.online) -> DeviceResponse:
	return DeviceResponse(
		device_id=uuid4(),
		name="test-router",
		device_type=DeviceType.router,
		ip_address="192.168.1.1",
		status=status,
	)


def test_registration(
	service_and_repository: tuple[DeviceService, InMemoryDeviceRepository],
) -> None:
	service, _ = service_and_repository
	device = make_device()

	registered = service.register(device)

	assert registered == device
	assert service.get(device.device_id) == device
	assert service.list() == [device]


def test_duplicate_registration_raises_error(
	service_and_repository: tuple[DeviceService, InMemoryDeviceRepository],
) -> None:
	service, _ = service_and_repository
	device = make_device()
	service.register(device)

	with pytest.raises(DeviceAlreadyExistsError):
		service.register(device)


def test_missing_device_raises_error(
	service_and_repository: tuple[DeviceService, InMemoryDeviceRepository],
) -> None:
	service, _ = service_and_repository
	missing_id = uuid4()

	with pytest.raises(DeviceNotFoundError):
		service.get(missing_id)

	with pytest.raises(DeviceNotFoundError):
		service.update_status(missing_id, DeviceStatus.offline)


def test_initial_offline_registration_does_not_create_alert(
	service_and_repository: tuple[DeviceService, InMemoryDeviceRepository],
) -> None:
	service, repository = service_and_repository
	device = make_device(DeviceStatus.offline)

	service.register(device)

	assert repository.list_alerts() == []


def test_online_to_offline_creates_one_utc_alert(
	service_and_repository: tuple[DeviceService, InMemoryDeviceRepository],
) -> None:
	service, repository = service_and_repository
	device = make_device()
	service.register(device)

	service.update_status(device.device_id, DeviceStatus.offline)

	alerts = repository.list_alerts()
	assert len(alerts) == 1
	assert alerts[0].device_id == device.device_id
	assert alerts[0].message == f"Device {device.device_id} went offline."
	assert alerts[0].timestamp.utcoffset() == timedelta(0)


def test_repeated_offline_update_does_not_create_another_alert(
	service_and_repository: tuple[DeviceService, InMemoryDeviceRepository],
) -> None:
	service, repository = service_and_repository
	device = make_device()
	service.register(device)

	service.update_status(device.device_id, DeviceStatus.offline)
	service.update_status(device.device_id, DeviceStatus.offline)

	assert len(repository.list_alerts()) == 1
