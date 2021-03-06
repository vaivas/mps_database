from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from models import Base

class Device(Base):
  """
  Device class (devices table)

  This is a generic class that contains properties common to DigitalDevices
  and AnalogDevices.

  Properties:
    name: unique device name (possibly MAD device name)
    description: some extra information about this device
    position: 100 to 999 number that defines approximatelly where the device
              is within the area. This field is used to create PVs
    area: sector where the device is installed (e.g. GUNB, LI30, DMPB,...), this
          is used to create the PVs (second field). This field is used
          to create PVs.
    evaluation: define if device state is evaluated by fast(1) or slow(0) logic.
                default value is slow(0)

  References:
    card_id: application card that owns this device

  """
  __tablename__ = 'devices'
  id = Column(Integer, primary_key=True)
  discriminator = Column('type', String(50))
  name = Column(String, unique=True, nullable=False)
  description = Column(String, nullable=False)
  position = Column(Integer, nullable=False)
  area = Column(String, nullable=False)
  evaluation = Column(Integer, nullable=False, default=0)
  card_id = Column(Integer, ForeignKey('application_cards.id'), nullable=False)
  device_type_id = Column(Integer, ForeignKey('device_types.id'), nullable=False)
  fault_outputs = relationship("FaultInput", backref='device')
  __mapper_args__ = {'polymorphic_on': discriminator}

class DigitalDevice(Device):  
  """
  DigitalDevice class (digital_devices table)

  Relationships:
   inputs: list of DeviceInput that use this DigitalDevice
   fault_outputs: list of FaultInputs that use this DigitalDevice as input
  """
  __tablename__ = 'digital_devices'
  __mapper_args__ = {'polymorphic_identity': 'digital_device'}
  id = Column(Integer, ForeignKey('devices.id'), primary_key=True)
  inputs = relationship("DeviceInput", backref='digital_device')
#  fault_outputs = relationship("FaultInput", backref='device')

class AnalogDevice(Device):
  """
  AnalogDevice class (analog_devices table)

  References:
    channel_id: reference to the AnalogChannel that is connected to
                to the actual device

  Relationships:
    threshold_faults: list of ThresholdFaults that reference
                      this AnalogDevice
  """
  __tablename__ = 'analog_devices'
  __mapper_args__ = {'polymorphic_identity': 'analog_device'}
  id = Column(Integer, ForeignKey('devices.id'), primary_key=True)
#  analog_device_type_id = Column(Integer, ForeignKey('analog_device_types.id'), nullable=False)
  channel_id = Column(Integer, ForeignKey('analog_channels.id'), nullable=False, unique=True)
#  threshold_faults = relationship("ThresholdFault", backref='analog_device')
