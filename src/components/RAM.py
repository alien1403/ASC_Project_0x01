class RAM:
    __INSTANCE = None

    # Implementare Singleton cu ajutorul unei metode statice
    @staticmethod
    def getInstance():
        if RAM.__INSTANCE is None:
            RAM.__INSTANCE = RAM()
        return RAM.__INSTANCE

    def __init__(self) -> None:
        super().__init__()
        # Stack-ul de memorie, inital gol
        self.__stack = []

    def __hexStrToInt(self, string):
        return int("0x{}".format(string), base=16)

    def loadInstructions(self, instructions):
        maxAddr = max(instructions.keys())
        minAddr = min(instructions.keys())
        stack_size = self.__hexStrToInt(maxAddr) - self.__hexStrToInt(minAddr)
        self.__stack = [0 for _ in range(stack_size + 1)]
        first_instr = True
        offset = 0
        for address, instruction in instructions.items():
            if first_instr:
                offset = self.__hexStrToInt(address)
            first_instr = False
            current_address = self.__hexStrToInt(address)
            current_instruction = self.__hexStrToInt(instruction)
            self.__stack[current_address - offset] = current_instruction

    # def getStack(self):
    #     return self.__stack

    # print(hex(self.__stack[0x2b84]))

    def getInstruction(self, location):
        return self.__stack[location]

    def getData(self, location):
        return self.__stack[location]

    def writeData(self, location, data):
        stack_size = len(self.__stack)
        needed_space = location - stack_size
        if needed_space > 0:
            self.__stack = self.__stack + [0 for _ in range(needed_space + 1)]

        self.__stack[location] = data
