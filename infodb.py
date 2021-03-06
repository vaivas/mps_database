from mps_config import MPSConfig, models
from sqlalchemy import func
import sys
import argparse

def showStats(name, session):
  "Print statistics from the specified database"
  print "Statistics for database " + args.database.name
#  print session.query(func.count('*')).select_from('crates').scalar()
  print "Crates            : " + str(session.query(func.count(models.Crate.id)).scalar())
  print "Cards             : " + str(session.query(func.count(models.ApplicationCard.id)).scalar())

  print "Device Types      : " + str(session.query(func.count(models.DeviceType.id)).scalar())
  print "Digital Devices   : " + str(session.query(func.count(models.DigitalDevice.id)).scalar())
  print "Digital Channels  : " + str(session.query(func.count(models.DigitalChannel.id)).scalar())

  print "Analog Devices    : " + str(session.query(func.count(models.AnalogDevice.id)).scalar())
  print "Analog Channels   : " + str(session.query(func.count(models.AnalogChannel.id)).scalar())

  print "Faults            : " + str(session.query(func.count(models.Fault.id)).scalar())
  print "FaultInputs       : " + str(session.query(func.count(models.FaultInput.id)).scalar())
  print "FaultStates       : " + str(session.query(func.count(models.FaultState.id)).scalar())

  print "IgnoreConditions  : " + str(session.query(func.count(models.IgnoreCondition.id)).scalar())
  print "Conditions        : " + str(session.query(func.count(models.Condition.id)).scalar())
  print "ConditionInputs   : " + str(session.query(func.count(models.ConditionInput.id)).scalar())

  print "Beam Classes      : " + str(session.query(func.count(models.BeamClass.id)).scalar())
  print "Allowed Classes   : " + str(session.query(func.count(models.AllowedClass.id)).scalar())
  print "Mitigation Devices: " + str(session.query(func.count(models.MitigationDevice.id)).scalar())

  return

parser = argparse.ArgumentParser(description='Print database information')
parser.add_argument('database', metavar='db', type=file, nargs='?', help='database file name (e.g. mps_gun.db)')
parser.add_argument('--stats', action="store_true", help='print database statistics (e.g. number of crates)')

args = parser.parse_args()
mps = MPSConfig(args.database.name)
session = mps.session

if (args.stats):
  showStats(args.database.name, session)

session.close()
exit(0)

if (len(sys.argv) == 2):
  file_name = sys.argv[1]
else:
  file_name = 'mps_gun_config.db'


print "+==================================================================+"
print "| Faults"
print "+==================================================================+"
for fault in session.query(models.Fault).all():
  print ""
  print "+------------------------------------------------------------------+"
  print "| [" + str(fault.id) + "] Fault: " + fault.name
  channelNames = []
  num_bits = 0
  for inp in fault.inputs:
    analog = False
    try:
      digitalDevice = session.query(models.DigitalDevice).filter(models.DigitalDevice.id==inp.device_id).one()
    except:
      analogDevice = session.query(models.AnalogDevice).filter(models.AnalogDevice.id==inp.device_id).one()
      analog = True

    if (analog == False):
      for ddi in digitalDevice.inputs:
        channel = session.query(models.DigitalChannel).filter(models.DigitalChannel.id==ddi.channel_id).one()
        card = session.query(models.ApplicationCard).filter(models.ApplicationCard.id==channel.card_id).one()
        crate = session.query(models.Crate).filter(models.Crate.id==card.crate_id).one()
        num_bits = num_bits + 1
        channelNames.append(channel.name + " - " + digitalDevice.description + " [crate: " + str(crate.number) +
                            ", slot: " + str(card.slot_number)+ ", channel: " + str(channel.number)+ "]")
    else:
      for state in fault.states:
        num_bits = num_bits + 1
        deviceState = session.query(models.DeviceState).filter(models.DeviceState.id==state.device_state_id).one()
        channel = session.query(models.AnalogChannel).filter(models.AnalogChannel.id==analogDevice.channel_id).one()
        card = session.query(models.ApplicationCard).filter(models.ApplicationCard.id==channel.card_id).one()
        crate = session.query(models.Crate).filter(models.Crate.id==card.crate_id).one()
        channelNames.append(deviceState.name + " [crate: " + str(crate.number) +
                            ", slot: " + str(card.slot_number)+ ", channel: " + str(channel.number)+ "]")
      

  print "+---------------+-----------------------+--------------------------+"
  print "| ",
  var = 'A'
  for b in range(0,num_bits):
    print var,
    var = chr(ord(var) + 1)
  print "State\t| Name\t\t\t| Mitigation"
  print "+---------------+-----------------------+--------------------------+"

  if (analog == False):
    for state in fault.states:
      print "| ",
      deviceState = session.query(models.DeviceState).filter(models.DeviceState.id==state.device_state_id).one()
      bits = []
      maskBits = []
      value = deviceState.value
      mask = deviceState.mask
      for b in range(0,num_bits):
        bits.append(value & 1)
        maskBits.append(mask & 1)
        value = (value >> 1)
        mask = (mask >> 1)
        if (maskBits[b] == 0):
          print '-',
        else:
          print bits[b],
      if (state.default == True):
        print "default",
      else:
        print "0x%0.4X" % deviceState.value, 
      print "\t| " + deviceState.name + "\t|",
      for c in state.allowed_classes:
        beamClass = session.query(models.BeamClass).filter(models.BeamClass.id==c.beam_class_id).one()
        mitigationDevice = session.query(models.MitigationDevice).filter(models.MitigationDevice.id==c.mitigation_device_id).one()
        print "[" + mitigationDevice.name + "@" + beamClass.name + "] ",
      print ""
  else:
    for state in fault.states:
      print "| ",
      deviceState = session.query(models.DeviceState).filter(models.DeviceState.id==state.device_state_id).one()
      bits = []
      maskBits = []
      anti_bits = []
      anti_mask = []
      value = deviceState.value
      mask = deviceState.mask
      for b in range(0,num_bits):
        anti_bits.append(value & 1)
        anti_mask.append(mask & 1)
        value = (value >> 1)
        mask = (mask >> 1)

      for b in range(0, num_bits):
        bits.append(anti_bits[num_bits-b-1])
        maskBits.append(anti_mask[num_bits-b-1])

      for b in range(0,num_bits):
        if (maskBits[b] == 1):
          print '-',
        else:
          print bits[b],
      if (state.default == True):
        print "default",
      else:
        print "0x%0.4X" % deviceState.value, 
      print "\t| " + deviceState.name + "\t|",
      for c in state.allowed_classes:
        beamClass = session.query(models.BeamClass).filter(models.BeamClass.id==c.beam_class_id).one()
        mitigationDevice = session.query(models.MitigationDevice).filter(models.MitigationDevice.id==c.mitigation_device_id).one()
        print "[" + mitigationDevice.name + "@" + beamClass.name + "] ",
      print ""
  print "+---------------+-----------------------+--------------------------+"

  if (analog == False):
    print "\nInputs:"
    var = 'A'
    for b in range(0,num_bits):
      print " " + var + ": " + channelNames[b]
      var = chr(ord(var) + 1)
  else:
    print "\nThresholds:"
    var = 'A'
    for b in range(0,num_bits):
      print " " + var + ": " + channelNames[b]
      var = chr(ord(var) + 1)

print ""

print "+==================================================================+"
print "| Ignore Logic"
print "+==================================================================+"
for condition in session.query(models.Condition).all():
  print ""
  print "+------------------------------------------------------------------+"
  print "| Condition: " + condition.name + " value: ",
  print "0x%0.4X" % condition.value
  print "+------------------------------------------------------------------+"
  for inp in condition.condition_inputs:
    faultState = session.query(models.FaultState).filter(models.FaultState.id==inp.fault_state_id).one()
    deviceState = session.query(models.DeviceState).filter(models.DeviceState.id==faultState.device_state_id).one()
    print "| bit " + str(inp.bit_position) + ": " + inp.fault_state.fault.name + ", value: " + str(deviceState.value)
  print "+------------------------------------------------------------------+"

  print "| Ignored Faults:"
  print "+------------------------------------------------------------------+"
  for ignore_fault in condition.ignore_conditions:
    if (hasattr(ignore_fault.fault_state, 'fault_id')):
      print "| " + "[" + str(ignore_fault.fault_state.fault_id) + "]\t" + ignore_fault.fault_state.fault.name + " (digital)"
    else:
      print "| " + "[" + str(ignore_fault.fault_state.threshold_fault_id) + "]\t",
      print ignore_fault.fault_state.threshold_fault.name + " (threshold)"
  print "+------------------------------------------------------------------+"
