from blinker import Namespace

leyan = Namespace()

after_boot = leyan.signal("AFTER-BOOT")
