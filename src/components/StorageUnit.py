import os
import sys
from src.components.RAM import RAM
from src.components.CPU import CPU

RAM = RAM.getInstance()
CPU = CPU.getInstance()


class StorageUnit:
    __INSTANCE = None

    def __init__(self) -> None:
        super().__init__()

    # Implementare Singleton cu ajutorul unei metode statice
    @staticmethod
    def getInstance():
        if StorageUnit.__INSTANCE is None:
            StorageUnit.__INSTANCE = StorageUnit()
        return StorageUnit.__INSTANCE

    def runExecutables(self):

        mc_files = ['./assets/mc/rv32ui-v-addi.mc',
                    './assets/mc/rv32ui-v-beq.mc',
                    './assets/mc/rv32ui-v-lw.mc',
                    './assets/mc/rv32ui-v-srl.mc',
                    './assets/mc/rv32ui-v-sw.mc',
                    './assets/mc/rv32ui-v-xor.mc',
                    './assets/mc/rv32um-v-rem.mc'
                    ]

        for mc_file in mc_files:
            instructions, data = self.__parseMcFile(mc_file)

            RAM.loadInstructions(instructions)
            RAM.loadData(data)

            print("Se ruleaza {}".format(mc_file.split('/')[-1]))
            CPU.execute()

            CPU.reset()
            RAM.reset()


    def __parseMcFile(self, mc_file):
        current_section = ".text"
        lastDataAddr = None
        instructions_dict = {}
        data_dict = {}
        file = open(mc_file, "r")
        for line in file.readlines():
            if ".data" in line:
                current_section = ".data"
            line = line.replace("\n", "")
            tokens = line.split(":")
            if len(tokens) == 2 and tokens[1] != '':
                if current_section == ".text":
                    instructions_dict[tokens[0]] = tokens[1].strip()
                elif current_section == ".data":
                    if lastDataAddr is None:
                        lastDataAddr = tokens[0]
                        data_dict[lastDataAddr] = tokens[1].strip()

                    elif int("0x{}".format(tokens[0]), base=16) - int("0x{}".format(lastDataAddr), base=16) == 2:
                        data_dict[lastDataAddr] = data_dict[lastDataAddr] + tokens[1].strip()
                    else:
                        data_dict[tokens[0]] = tokens[1].strip()
                        lastDataAddr = tokens[0]
        return instructions_dict, data_dict
