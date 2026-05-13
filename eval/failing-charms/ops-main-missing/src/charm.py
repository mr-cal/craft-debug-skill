#!/usr/bin/env python3
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)

    def _on_install(self, event):
        self.unit.status = ops.ActiveStatus()

if __name__ == "__main__":
    # Oops - forgot to call ops.main(MyCharm)
    print("Starting charm...")
