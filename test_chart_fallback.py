import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(r"D:\PROYECTOS PROGRAMACIÓN\ANTIGRAVITY_PROJECTS\app_func_v2")

from modules.chart_utils import generate_fallback_charts_batch

def test_sex_counts_fallback():
    data = {
        'sex_counts': pd.DataFrame({
            'Género': ['Masculino', 'Femenino'],
            'Cantidad': [10, 15]
        })
    }
    
    print("Generating charts...")
    paths = generate_fallback_charts_batch(data)
    
    if 'sex_counts' in paths:
        print(f"SUCCESS: sex_counts generated at {paths['sex_counts']}")
        if os.path.exists(paths['sex_counts']):
            print("Verified file exists.")
        else:
            print("ERROR: File does not exist.")
    else:
        print("ERROR: sex_counts not found in return paths.")

if __name__ == "__main__":
    test_sex_counts_fallback()
