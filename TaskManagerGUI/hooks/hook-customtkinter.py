from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from the customtkinter package
datas = collect_data_files('customtkinter')

# Collect all submodules from the unicodedata package
hiddenimports = collect_submodules('unicodedata')
