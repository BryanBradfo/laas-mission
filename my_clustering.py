#Distance binaire
#créer un dictionnaire
#clé: nom de la ville
#valeur: liste des villes les plus proches

dict = {}
#addding a key value pair
dict["Paris"] = ["Lyon", "Marseille", "Toulouse"]
#adding without key
dict.update({"tlse": ["Lyon", "Marseille", "Toulouse"]})

print(dict)
