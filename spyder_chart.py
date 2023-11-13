import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Créez un DataFrame avec les données du profil
data = {
    'Python': [4, 5, 3, 2],
    'Charimse': [3, 4, 5, 2],
    'Kaaris': [2, 3, 4, 3],
    'Coupe de cheveux': [4, 3, 5, 4]
}

df = pd.DataFrame(data)

# Définissez le nom de la personne (optionnel)
person_name = "Luc Charlopeau"

# Nombre de caractéristiques (colonnes)
num_features = len(df.columns)

# Créez un graphique radar
fig, ax = plt.subplots(subplot_kw={'polar': True})

# Liste des noms de caractéristiques (colonnes)
feature_names = df.columns

# Les angles pour chaque caractéristique
angles = np.linspace(0, 2 * np.pi, num_features, endpoint=False).tolist()
angles += angles[:1]

# Les valeurs pour la première personne (à modifier si vous avez plusieurs profils)
values = df.iloc[0].values.tolist()
values += values[:1]

# Tracez le graphique radar
ax.fill(angles, values, 'b', alpha=0.1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(feature_names)
ax.set_title(person_name)

# Affichez le graphique radar
plt.show()