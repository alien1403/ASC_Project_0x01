class StorageUnit:
    __INSTANCE = None

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def getInstance():
        if StorageUnit.__INSTANCE is None:
            StorageUnit.__INSTANCE = StorageUnit()
        return StorageUnit.__INSTANCE

    def getExecutables(self):
        return ['./assets/mc/rv32ui-v-addi.mc',
                './assets/mc/rv32ui-v-beq.mc',
                './assets/mc/rv32ui-v-lw.mc',
                './assets/mc/rv32ui-v-srl.mc',
                './assets/mc/rv32ui-v-sw.mc',
                './assets/mc/rv32ui-v-xor.mc',
                './assets/mc/rv32um-v-rem.mc'
                ]
