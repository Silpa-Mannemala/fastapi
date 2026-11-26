from uuid import UUID

from app.events import create_offline_alert
from app.models import AlertResponse, DeviceResponse, DeviceStatus
from app.repositories.device_repository import InMemoryDeviceRepository


class DeviceAlreadyExistsError(Exception):
	pass


class DeviceNotFoundError(Exception):
	pass


class DeviceService:
	def __init__(self, repository: InMemoryDeviceRepository) -> None:
		self._repository = repository

	def register(self, device: DeviceResponse) -> DeviceResponse:
		if self._repository.get_device(device.device_id) is not None:
			raise DeviceAlreadyExistsError(
				f"Device {device.device_id} is already registered"
			)
		return self._repository.add_device(device)

	def list_alerts(self) -> list[AlertResponse]:
		return self._repository.list_alerts()

	def list(self) -> list[DeviceResponse]:
		return self._repository.list_devices()

	def get(self, device_id: UUID) -> DeviceResponse:
		device = self._repository.get_device(device_id)
		if device is None:
			raise DeviceNotFoundError(f"Device {device_id} was not found")
		return device

	def update_status(
		self, device_id: UUID, status: DeviceStatus
	) -> DeviceResponse:
		current_device = self.get(device_id)
		updated_device = self._repository.update_status(device_id, status)
		if updated_device is None:
			raise DeviceNotFoundError(f"Device {device_id} was not found")

		if (
			current_device.status is DeviceStatus.online
			and updated_device.status is DeviceStatus.offline
		):
			create_offline_alert(self._repository, device_id)

		return updated_device
