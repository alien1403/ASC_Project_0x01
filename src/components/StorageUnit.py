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

    '''
    Obtinem toate "executabilele" (fisierele .mc) de pe "disc" (adica din folderul assets/mc) si le parsam 
    in asa fel incat sa contina doar instructiunile ce trebuie executate. 
    Aceste instructiuni vor fi incarcate in RAM si procesorul le va executa
    '''

    def getExecutables(self):
        """
        Pentru inceput, obtinem instructiunile doar pentru primul executabil
        """

        # TODO Inlocuieste cu path-urile relative la root-ul proiectului
        mc_file = '/home/liviu/Desktop/asc/ASC_0x01_Project/assets/mc/rv32ui-v-srl.mc'

        instructions, data = self.__parseMcFile(mc_file)
        '''
            Acum incarcam in RAM instructiunile din executabil
            Pentru ca "RAM-ul" nostru e virtualizat si nu are de a face cu vreun sistem hardware real,
            adresa primei instructiuni din mc este irelevanta - putem incepe de la 0 (pentru a nu folosi 
            degeaba resurse din adevaratul RAM :)))
        '''

        RAM.loadInstructions(instructions)
        RAM.loadData(data)
        CPU.execute()


        '''
        Dupa ce incarc instructiunile in RAM, CPU-ul le va executa
        '''

    def getContents(self) -> str:
        return "Storage Unit Contents"

    '''
        Returnam instructiunile sub forma de dictionar, cheia fiind adresa de memorie 
        si valoarea fiind instructiunea in sine
        
        Pentru ca .mc-ul este in sine un dump, mai contine ceva metadata de care trebuie sa scapam 
        Parsam fisierul si pastram doar liniile care sunt de forma 
        <numar_hexa_pe_32_de_biti>:<spatii><<numar_hexa_pe_32_de_biti>
        Primul numar hexa reprezinta adresa din memorie, al doilea numar hexa reprezinta instructiunea
        ce trebuie executata de catre procesor
        
    '''

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
