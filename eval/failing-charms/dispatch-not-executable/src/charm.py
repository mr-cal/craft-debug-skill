#!/usr/bin/env python3
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)

if __name__ == "__main__":
    ops.main(MyCharm)
