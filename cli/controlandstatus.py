# Statuses
NRTSO = 0x0000  # not ready to switch on
NRTSO_MASK = 0x004f
SOD = 0x0040  # switch on disabled
SOD_MASK = 0x004f
RTSO = 0x0021  # ready to switch on
RTSO_MASK = 0x006f
SO = 0x0023  # switched on
SO_MASK = 0x006f
OE = 0x0027  # operation enabled
OE_MASK = 0x006f
QSA = 0x0007  # quick stop active
QSA_MASK = 0x006f
FRA = 0x004f  # fault reaction active
FRA_MASK = 0x004f
FAULT = 0x0008  # Fault
FAULT_MASK = 0x004f

# Control commands
CTL_SHDWN = 0x0006  # "Shutdown"
CTL_SO = 0x0007  # "Switch on"
CTL_DISVOLT = 0x0000  # "Disable Voltage"
CTL_QUICKST = 0x0002  # "Quick Stop"
CTL_DISOP = 0x0007  # "Disable Operation"
CTL_ENOP = 0x000f  # "Enable operation"
CTL_ENOPAQST = 0x000f  # "Enable operation after Quick stop"
CTL_RST = 0x0080  # "Fault/Warning Reset"

# Status dictionary
status_dict = {
    "NRTSO": {"value": 0x0000, "mask": 0x004f, "display": "Not ready to switch on", "color": "#FF00FF"},
    "SOD": {"value": 0x0040, "mask": 0x004f, "display": "Switch on disabled", "color": "#FFA500"},
    "RTSO": {"value": 0x0021, "mask": 0x006f, "display": "Ready to switch on", "color": "#004000"},
    "SO": {"value": 0x0023, "mask": 0x006f, "display": "Switched on", "color": "#008000"},
    "OE": {"value": 0x0027, "mask": 0x006f, "display": "Operation enabled", "color": "#00FF00"},
    "QSA": {"value": 0x0007, "mask": 0x006f, "display": "Quick stop active", "color": "#4B0082"},
    "FRA": {"value": 0x004f, "mask": 0x004f, "display": "Fault reaction active", "color": "#9400D3"},
    "FAULT": {"value": 0x0008, "mask": 0x004f, "display": "Fault", "color": "#FF0000"},
}


def det_status(val):
    for name, info in status_dict.items():
        if info["value"] == (val & info["mask"]):
            return name, info["display"], info["color"]
    return "NONE", "Unknown status", "#FFFFFF"


def _det_status(val):
    if NRTSO == (val & NRTSO_MASK):
        return NRTSO
    elif SOD == (val & SOD_MASK):
        return SOD
    elif RTSO == (val & RTSO_MASK):
        return RTSO
    elif SO == (val & SO_MASK):
        return SO
    elif OE == (val & OE_MASK):
        return OE
    elif QSA == (val & QSA_MASK):
        return QSA
    elif FRA == (val & FRA_MASK):
        return FRA
    elif FAULT == (val & FAULT_MASK):
        return FAULT
    else:
        return -1
