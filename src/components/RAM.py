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
        self.__STACK_OFFSET = 0
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
        for address, instruction in instructions.items():
            if first_instr:
                self.__STACK_OFFSET = self.__hexStrToInt(address)
            first_instr = False
            current_address = self.__hexStrToInt(address)
            current_instruction = self.__hexStrToInt(instruction)
            self.__stack[current_address - self.__STACK_OFFSET] = current_instruction

    def loadData(self, dataDict):
        if len(dataDict) == 0:
            return []
        maxAddr = max(dataDict.keys())
        maxAddr = self.__hexStrToInt(maxAddr)
        minAddr = len(self.__stack) + self.__STACK_OFFSET
        needed_space = (maxAddr - minAddr)
        self.__stack = self.__stack + [0 for _ in range(needed_space + 1)]

        for address, data in dataDict.items():
            current_address = self.__hexStrToInt(address)
            current_data = self.__hexStrToInt(data)
            self.__stack[current_address - self.__STACK_OFFSET] = current_data

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
