import ipaddress
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceType(str, Enum):
	router = "router"
	switch = "switch"
	server = "server"


class DeviceStatus(str, Enum):
	online = "online"
	offline = "offline"


class _DeviceFields(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	device_type: DeviceType
	ip_address: str
	status: DeviceStatus = DeviceStatus.online

	@field_validator("ip_address")
	@classmethod
	def validate_ipv4(cls, value: str) -> str:
		try:
			address = ipaddress.ip_address(value)
		except ValueError as error:
			raise ValueError("ip_address must be a valid IPv4 address") from error

		if not isinstance(address, ipaddress.IPv4Address):
			raise ValueError("ip_address must be an IPv4 address")
		return str(address)


class DeviceCreate(_DeviceFields):
	model_config = ConfigDict(
		json_schema_extra={
			"examples": [
				{
					"name": "office-router",
					"device_type": "router",
					"ip_address": "192.168.1.1",
					"status": "online",
				}
			]
		}
	)


class DeviceResponse(_DeviceFields):
	device_id: UUID


class StatusUpdate(BaseModel):
	model_config = ConfigDict(
		json_schema_extra={"examples": [{"status": "offline"}]}
	)

	status: DeviceStatus


class AlertResponse(BaseModel):
	device_id: UUID
	message: str
	timestamp: datetime