import discord


class Tormenta20_Character:
    def __init__(self, nome, classe, level):
        self.system = "Tormenta 20"
        self.image = ("https://publicdomainvectors.org/photos/abstract-user-"
                      "flat-1.png")
        self.nome = nome
        self.classe = classe
        self.level = level
        self.description = 0
        self.experience = 0
        self.raça = ""
        self.origem = ""
        self.divindade = ""

        self.força = 10
        self.destreza = 10
        self.constituição = 10
        self.inteligência = 10
        self.sabedoria = 10
        self.carisma = 10

        self.pontos_de_vida = 0
        self.pontos_de_vida_máximos = 0
        self.pontos_de_mana = 0
        self.pontos_de_mana_máximos = 0

        self.defesa = 0

        self.proficiências = "None"
        self.tamanho = "Médio"
        self.deslocamento = "None"

        self.acrobacia = 0
        self.adestramento = 0
        self.atletismo = 0
        self.atuação = 0
        self.cavalgar = 0
        self.conhecimento = 0
        self.cura = 0
        self.diplomacia = 0
        self.enganação = 0
        self.fortitude = 0
        self.furtividade = 0
        self.guerra = 0
        self.iniciativa = 0
        self.intimidação = 0
        self.intuição = 0
        self.investigação = 0
        self.jogatina = 0
        self.ladinagem = 0
        self.luta = 0
        self.misticismo = 0
        self.nobreza = 0
        self.percepção = 0
        self.pilotagem = 0
        self.pontaria = 0
        self.reflexos = 0
        self.religião = 0
        self.sobrevivência = 0
        self.vontade = 0
        self.ofício_adicional_1_nome = ""
        self.ofício_adicional_1 = 0
        self.ofício_adicional_2_nome = ""
        self.ofício_adicional_2 = 0

        self.inventory = ""
        self.currency = 0

        self.habilidades_de_raça_e_origem = ""
        self.habilidades_de_classe_e_poderes = ""
