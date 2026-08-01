import sys
import traceback
try:
    import apps.api.main
    print("Success")
except Exception as e:
    print("Error during import:")
    traceback.print_exc()
