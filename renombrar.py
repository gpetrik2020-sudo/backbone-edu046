import os
import unicodedata

DIR = 'textos_md_edu046'

def limpiar(nombre):
    # Quitar acentos
    nfkd = unicodedata.normalize('NFKD', nombre)
    sin_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Reemplazar espacios por guiones bajos
    return sin_acentos.replace(' ', '_')

renombres = {}
for f in os.listdir(DIR):
    if f.endswith('.md'):
        nuevo = limpiar(f)
        if nuevo != f:
            os.rename(os.path.join(DIR, f), os.path.join(DIR, nuevo))
            renombres[f] = nuevo
            print(f"✓ {f} → {nuevo}")

print(f"\nTotal renombrados: {len(renombres)}")

# Actualizar app.py
with open('app.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

for viejo, nuevo in renombres.items():
    contenido = contenido.replace(viejo, nuevo)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(contenido)

print("✓ app.py actualizado")
