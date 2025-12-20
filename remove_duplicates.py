import sys
import os
sys.path.append(os.getcwd())
from firebase_bd import leer_registro, borrar_registro, actualizar_registro

print("--- DUPLICATE REMOVAL SCRIPT ---")
users = leer_registro('usuarios')
normalized_map = {}
duplicates_to_delete = []

# 1. Identify Duplicates
for uid, u in users.items():
    raw_rut = u.get('RUT', '')
    if not raw_rut: continue
    
    clean_rut = str(raw_rut).replace('.', '').strip()
    
    if clean_rut in normalized_map:
        # We found a duplicate!
        existing_entry = normalized_map[clean_rut]
        
        # Decide which one to keep:
        # Prefer the one WITHOUT dots if possible, OR the one with more content?
        # Actually, we want to KEEP the one that matches '18581575-7' (no dots) if it exists.
        
        entry_rut_is_clean = (existing_entry['rut'] == clean_rut)
        curr_rut_is_clean = (raw_rut == clean_rut)
        
        if entry_rut_is_clean and not curr_rut_is_clean:
            # Keep existing, delete current
            duplicates_to_delete.append(uid)
            print(f"Marking for deletion: {raw_rut} (ID: {uid}) - Duplicate of {existing_entry['rut']}")
        elif not entry_rut_is_clean and curr_rut_is_clean:
            # Keep current, delete existing
            duplicates_to_delete.append(existing_entry['id'])
            print(f"Marking for deletion: {existing_entry['rut']} (ID: {existing_entry['id']}) - Duplicate of {raw_rut}")
            # Update map to point to current (the keeper)
            normalized_map[clean_rut] = {'id': uid, 'rut': raw_rut}
        else:
            # Both dirty or both clean? Delete the current one (arbitrary)
            duplicates_to_delete.append(uid)
            print(f"Marking for deletion: {raw_rut} (ID: {uid}) - Arbitrary duplicate of {existing_entry['rut']}")
            
    else:
        normalized_map[clean_rut] = {'id': uid, 'rut': raw_rut}

print(f"Found {len(duplicates_to_delete)} duplicates to remove.")

# 2. Delete Duplicates
for uid in duplicates_to_delete:
    print(f"Deleting user ID: {uid}...")
    borrar_registro('usuarios', uid)

print("--- CLEANUP COMPLETE ---")
