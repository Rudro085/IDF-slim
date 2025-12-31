from templates.ebl.ebl import Ebl
from templates.midland.midland import Midland
from templates.mtb.mtb import Mtb
from templates.sonali.sonali import Sonali
from templates.ucb.ucb import Ucb

AvailableBanks = {
    "EBL" : Ebl(),
    "Midland" : Midland(),
    "MTB" : Mtb(),
    "Sonali" : Sonali(),
    "UCB" : Ucb() 
}