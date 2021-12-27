import sys
from src.components.RAM import RAM

RAM = RAM.getInstance()


class CPU:
    __INSTANCE = None

    # Implementare Singleton cu ajutorul unei metode statice
    @staticmethod
    def getInstance():
        if CPU.__INSTANCE is None:
            CPU.__INSTANCE = CPU()
        return CPU.__INSTANCE

    # Registrii procesorului, memorati ca dictionar (cheile sunt numele ABI ale registrilor)
    # Starea initiala  - 0 peste tot
    registers = {
        'zero': 0,  # hardwired, x0
        'ra': 0,  # x1
        'sp': 0,  # x2
        'gp': 0,  # x3
        'tp': 0,  # x4
        't0': 0,  # x5
        't1': 0,  # x6
        't2': 0,  # x7
        's0': 0,  # x8
        's1': 0,  # x9
        'a0': 0,  # x10
        'a1': 0,  # x11
        'a2': 0,  # x12
        'a3': 0,  # x13
        'a4': 0,  # x14
        'a5': 0,  # x15
        'a6': 0,  # x16
        'a7': 0,  # x17
        's2': 0,  # x18
        's3': 0,  # x19
        's4': 0,  # x20
        's5': 0,  # x21
        's6': 0,  # x22
        's7': 0,  # x23
        's8': 0,  # x24
        's9': 0,  # x25
        's10': 0,  # x26
        's11': 0,  # x27
        't3': 0,  # x28
        't4': 0,  # x29
        't5': 0,  # x30
        't6': 0,  # x31
        'pc': 0  # program counter
    }

    decoder = {
        'instruction': 0,
        'opcode': 0,
        'imm': 0,
        'rd': 0,
        'rs1': 0,
        'rs2': 0,
        'funct3': 0,
        'SIGINT': False
    }

    def __init__(self) -> None:
        self.__DEBUG_MODE = '--v' in sys.argv or True
        super().__init__()

    def execute(self):
        counter = 0

        while True:
            #if self.decoder['SIGINT'] or counter > 10000:
            if self.decoder['SIGINT'] or counter > 10000:
                break

            self.decoder = {
                'instruction': 0,
                'opcode': 0,
                'imm': 0,
                'rd': 0,
                'rs1': 0,
                'rs2': 0,
                'SIGINT': False
            }

            self.instructionFetch()
            self.instructionDecode()
            self.instructionExecute()
            counter += 1

            # Componentele MEM si WB ale ciclului vor fi initate de EX in cazul in care este necesar
            # Concret, instructionExecute va apela memoryAccess pt a obtine date din memorie / writeBack
            # pentru a scrie date in memorie - daca este cazul
            # self.memoryAccess(location)
            # self.writeBack(location, data)

            if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                print(("=" * 10 + "\n") * 4)

            counter += 1

    # TODO foloseste pt instructiunea curenta un registru
    # (de exemplu ) sp
    def instructionFetch(self):
        self.decoder['instruction'] = RAM.getInstruction(self.registers['pc'])
        if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
            print(self.registers)
            print("Instructiunea este:{}(decimal) = {}(hexa), adresa este {}(hexa)".format(self.decoder['instruction'],
                                                                                           hex(self.decoder[
                                                                                                   'instruction']),
                                                                                           hex(self.registers[
                                                                                                   'pc'] + 0x80000000)))

    '''
        Instructiuni implementate pana acum:

        - jal 
        - addi
        - ori
        - lui
        - auipc
        - lw
        - bne
        - beq
        - nop
        -slli
        -beqz
        
        
         Nu am implementat 
         - sectiunea .data??? wtf
         -fsw
         -srl
    '''

    def instructionDecode(self):
        binaryStringInstruction = bin(self.decoder['instruction'])[2:].zfill(0x20)
        opcodeBin = binaryStringInstruction[-7:]
        if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
            print(bin(self.decoder['instruction'])[2:].zfill(0x20))
        opcode = int(opcodeBin, base=2)
        self.decoder['opcode'] = opcode

        # opcode == 111 (jal)
        if opcode == 0x6F:
            # JAL => Instructiune J-Type
            imm = binaryStringInstruction[10:0:-1] + binaryStringInstruction[11:12] + binaryStringInstruction[
                                                                                      19:11:-1] + binaryStringInstruction[
                                                                                                  0:1]
            imm = imm[::-1]
            sign = -1 if imm[0] == '1' else 1
            offset = int(imm, base=2)
            if sign == -1:
                offset -= (1 << 19)
                offset = -offset
            offset = offset << 1
            self.decoder['imm'] = offset

        elif opcode == 0x13 or opcode == 0x3:
            # Instructiune I-Type
            # Extrag funct3-ul
            funct3 = (self.decoder['instruction'] & 0x7000) >> 0xC
            rd = (self.decoder['instruction'] & 0xf80) >> 7
            rs1 = (self.decoder['instruction'] & 0xf8000) >> 0xF
            imm = (self.decoder['instruction'] & 0xfff00000) >> 0x14
            # imm este in complement fata de 2, deci inversam semnul lui imm[11]*2^11
            imm = (imm & 0x7ff) - (imm & 0x800)

            self.decoder['funct3'] = funct3
            self.decoder['rd'] = rd
            self.decoder['rs1'] = rs1
            self.decoder['imm'] = imm

        elif opcode == 0x37 or opcode == 0x17:
            # LUI / AUIPC => Instructiune U-Type
            # Decodam rd-ul si imm-ul de la LUI si AUIPC la fel
            rd = (self.decoder['instruction'] & 0xf80) >> 7
            imm = (self.decoder['instruction'] & 0xfffff000) >> 0xC
            self.decoder['rd'] = rd
            self.decoder['imm'] = imm
        elif opcode == 0x63:
            # BEQ / BNE => Instructiune B-Type

            rs1 = (self.decoder['instruction'] & 0xf8000) >> 0xF
            rs2 = (self.decoder['instruction'] & 0x1f00000) >> 0x14
            funct3 = (self.decoder['instruction'] & 0x7000) >> 0xC

            imm_string = binaryStringInstruction[23:19:-1] + binaryStringInstruction[6:0:-1] + binaryStringInstruction[
                24] + binaryStringInstruction[0]
            imm_string = imm_string[::-1]

            imm = int(imm_string, base=2)
            # imm este in complement fata de 2, deci inversam semnul lui imm[11]*2^11
            imm = (imm & 0x7ff) - (imm & 0x800)

            # TREBUIE SA SARA 2 * offset

            self.decoder['funct3'] = funct3
            self.decoder['rs1'] = rs1
            self.decoder['rs2'] = rs2
            self.decoder['imm'] = imm

        elif opcode == 0x73:
            # Sfarsitul programului, daca a0 e 1 atunci suntem pe pass,
            # altfel pe fail
            if self.registers['a0'] == 1:
                print("pass")
            else:
                print("fail")

            self.decoder['SIGINT'] = True
        if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
            print("Opcode is {} (decimal) / {} (binary)".format(opcode, bin(opcode)[2:]))

    def instructionExecute(self):
        # opcode == 111 (jal)
        if self.decoder['opcode'] == 0x6F:
            self.registers['pc'] += self.decoder['imm']
        # opcode == 19
        elif self.decoder['opcode'] == 0x13:
            # addi
            if self.decoder['funct3'] == 0:

                rdKey = self.__getRegisterKeyByIdx(self.decoder['rd'])
                rs1Key = self.__getRegisterKeyByIdx(self.decoder['rs1'])

                if rdKey != 'zero':
                    # Simulare overflow
                    self.registers[rdKey] = (self.registers[rs1Key] + self.decoder['imm']) & 0xFFFFFFFF
                    # Simulare complement fata de 2, deci inversam semnul lui reg[31]*2^11

                    self.registers[rdKey] = (self.registers[rdKey] & 0x7fffffff) - (self.registers[rdKey] & 0x80000000)

                if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                    print(
                        "registers[{}] = {} ({} + {}) ADDI".format(rdKey, self.registers[rs1Key] + self.decoder['imm'],
                                                                   self.registers[rs1Key], self.decoder['imm']))

            # ori
            elif self.decoder['funct3'] == 6:
                rdKey = self.__getRegisterKeyByIdx(self.decoder['rd'])
                rs1Key = self.__getRegisterKeyByIdx(self.decoder['rs1'])
                if rdKey != 'zero':
                    self.registers[rdKey] = self.registers[rs1Key] | self.decoder['imm']
                if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                    print("registers[{}] = {} ({} | {}) ORI".format(rdKey, self.registers[rs1Key] | self.decoder['imm'],
                                                                    self.registers[rs1Key], self.decoder['imm']))
            # slli
            elif self.decoder['func3'] == 0:
                '''
                    In cazul instructiunilor de shift, cei 
                    mai nesemnificativi 5 biti ai imm-ului reprezinta shamt_i
                    aka valoarea cu care trebuie shiftat rs1 si mai apoi 
                    sa fie stocat in rd
                '''
                shamt_i = self.decoder['imm'] & 0x1F
                rdKey = self.__getRegisterKeyByIdx(self.decoder['rd'])
                rsKey = self.__getRegisterKeyByIdx(self.decoder['rs1'])

                if rdKey != 'zero':
                    self.registers[rdKey] = ((self.registers[rsKey] << shamt_i) & 0xFFFFFFFF)

            self.registers['pc'] += 4
        elif self.decoder['opcode'] == 0x3:
            # lw
            if self.decoder['funct3'] == 2:
                rdKey = self.__getRegisterKeyByIdx(self.decoder['rd'])
                rs1Key = self.__getRegisterKeyByIdx(self.decoder['rs1'])

                memAddr = self.decoder['imm'] + self.registers[rs1Key]
                memAddrValue = self.memoryAccess(memAddr)
                # Valoarea din memorie e reprezentata in complement
                # fata de 2, deci trebuie sa inversam semnul lui
                # memAddrValue[31] * 2^31

                # TODO Trebuie sa avem grija cand punem valori in memorie (sa nu fie negative)
                # pt ca le luam deja pozitive
                memAddrValue = (memAddrValue & 0x7fffffff) - (memAddrValue & 0x80000000)
                if rdKey != 'zero':
                    self.registers[rdKey] = memAddrValue
            self.registers['pc'] += 4
        elif self.decoder['opcode'] == 0x63:
            # beq
            if self.decoder['funct3'] == 0:
                # Trebuie sa sara la 2*offset daca rs1 == rs2
                rs1Key = self.__getRegisterKeyByIdx(self.decoder['rs1'])
                rs2Key = self.__getRegisterKeyByIdx(self.decoder['rs2'])
                offset = 2 * self.decoder['imm']
                if self.registers[rs1Key] == self.registers[rs2Key]:
                    self.registers['pc'] += offset
                    if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                        print("BEQ")
                # daca nu e jump, doar trece la urm instr
                else:
                    self.registers['pc'] += 4

            # bne
            elif self.decoder['funct3'] == 1:
                # Trebuie sa sara la 2*offset daca rs1 != rs2
                rs1Key = self.__getRegisterKeyByIdx(self.decoder['rs1'])
                rs2Key = self.__getRegisterKeyByIdx(self.decoder['rs2'])
                offset = 2 * self.decoder['imm']
                if self.registers[rs1Key] != self.registers[rs2Key]:
                    self.registers['pc'] += offset
                    if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                        print("BNE")
                # daca nu e jump, doar trece la urm instr
                else:
                    self.registers['pc'] += 4
        # LUI => Instructiune U-Type
        elif self.decoder['opcode'] == 0x37:
            rdKey = self.__getRegisterKeyByIdx(self.decoder['rd'])
            # Punem in cei mai semnificativi 20 de biti ai lui id imm-ul
            if rdKey != 'zero':
                self.registers[rdKey] = self.decoder['imm'] << 0xC

                # Simulare complement fata de 2, deci inversam semnul lui reg[31]*2^11

                self.registers[rdKey] = (self.registers[rdKey] & 0x7fffffff) - (self.registers[rdKey] & 0x80000000)

            if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                print("registers[{}] = {} ({} << 12) LUI".format(rdKey, self.decoder['imm'] << 0xC,
                                                                 self.decoder['imm']))

            self.registers['pc'] += 4
        # AUIPC => Instructiune U-Type
        elif self.decoder['opcode'] == 0x17:
            rdKey = self.__getRegisterKeyByIdx(self.decoder['rd'])
            imm_u = self.decoder['imm'] << 0xC
            imm_u += self.registers['pc']
            if rdKey != 'zero':
                self.registers[rdKey] = imm_u
            if self.__DEBUG_MODE and self.decoder['instruction'] != 0:
                print("registers[{}] = {} ({} + {}(program_counter)) AUIPC".format(rdKey, imm_u,
                                                                                   (self.decoder['imm'] << 0xC),
                                                                                   self.registers['pc']))

            self.registers['pc'] += 4


        else:
            self.registers['pc'] += 4

    def memoryAccess(self, location):
        return RAM.getData(location)

    def writeBack(self, location, data):
        RAM.writeData(location, data)

    def __getRegisterKeyByIdx(self, index):
        return list(self.registers.keys())[index]

    '''
    Deoarece toate instructiunile RV32I au rd-ul in instr[7:11] putem scrie o metoda care sa 
    il extraga pt a nu duplica prea mult cod

    '''

    def __extractRD(self, instruction):
        return (instruction & 0xf80) >> 7

    # Similar pt imm rs1 si rs2

    '''
    Nu e folosit pt instruciuni J-Type care au imm-ul construit diferit
    '''

    def __extractIMM(self, instruction):
        return (instruction & 0xfff00000) >> 0x14

    def __extractFunct3(self, instruction):
        return (instruction & 0x7000) >> 0xC

    def __extractRS1(self, instruction):
        return (instruction & 0xf8000) >> 0xF
